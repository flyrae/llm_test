"""批量测试API"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
import json
from datetime import datetime
import asyncio

from app.utils.database import get_db
from app.models.model_config import ModelConfigDB
from app.models.test_case import TestCaseDB
from app.models.test_result import TestResultDB, TestMetrics
from app.models.tool_definition import ToolDefinitionDB
from app.services.llm_service import LLMService
from app.services.agent_service import AgentService
from app.services.evaluation_service import EvaluationService
from app.config import settings

router = APIRouter()


class BatchRunRequest(BaseModel):
    """批量测试请求"""
    model_config = {"protected_namespaces": ()}
    
    model_ids: List[int] = Field(..., min_items=1, description="模型ID列表")
    test_case_ids: List[int] = Field(..., min_items=1, description="测试用例ID列表")
    params: Optional[Dict[str, Any]] = Field(None, description="覆盖模型参数")


class BatchRunResponse(BaseModel):
    """批量测试响应"""
    batch_id: str
    status: str
    message: str


class TestResultSummary(BaseModel):
    """测试结果摘要"""
    model_config = {"protected_namespaces": ()}
    
    test_case_id: int
    test_case_title: str
    model_id: int
    model_name: str
    output: str
    metrics: Dict[str, Any]
    score: Optional[float]
    status: str
    error_message: Optional[str]
    executed_at: datetime


class CompareResult(BaseModel):
    """对比结果"""
    test_case_id: int
    test_case_title: str
    results: List[Dict[str, Any]]


@router.post("/run", response_model=BatchRunResponse)
async def run_batch_test(
    request: BatchRunRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """执行批量测试"""
    # 验证模型和测试用例存在
    models = db.query(ModelConfigDB).filter(ModelConfigDB.id.in_(request.model_ids)).all()
    if len(models) != len(request.model_ids):
        raise HTTPException(status_code=404, detail="Some models not found")
    
    test_cases = db.query(TestCaseDB).filter(TestCaseDB.id.in_(request.test_case_ids)).all()
    if len(test_cases) != len(request.test_case_ids):
        raise HTTPException(status_code=404, detail="Some test cases not found")
    
    # 生成批次ID
    batch_id = f"batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # 在后台执行测试
    background_tasks.add_task(
        execute_batch_test,
        batch_id,
        models,
        test_cases,
        request.params
    )
    
    return BatchRunResponse(
        batch_id=batch_id,
        status="running",
        message=f"Batch test started with {len(models)} models and {len(test_cases)} test cases"
    )


async def execute_batch_test(
    batch_id: str,
    models: List[ModelConfigDB],
    test_cases: List[TestCaseDB],
    params: Optional[Dict[str, Any]]
):
    """执行批量测试（后台任务）"""
    from app.utils.database import SessionLocal
    
    db = SessionLocal()
    results = []
    
    try:
        for test_case in test_cases:
            # 加载测试用例关联的工具定义
            tools = None
            tools_config = {}
            if test_case.tools:
                tool_definitions = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.id.in_(test_case.tools)).all()
                # 转换为OpenAI API格式
                tools = [
                    {
                        "type": "function",
                        "function": {
                            "name": tool.name,
                            "description": tool.description,
                            "parameters": tool.parameters
                        }
                    }
                    for tool in tool_definitions
                ]
                # 构建工具配置字典（用于mock）
                tools_config = {tool.name: tool.mock_responses for tool in tool_definitions}
            
            for model in models:
                # 判断是否使用Agent模式
                # 如果测试用例配置了use_mock或有工具定义，使用Agent模式
                use_agent_mode = tools is not None
                use_mock = test_case.use_mock if test_case.use_mock is not None else False
                
                if use_agent_mode:
                    # 使用Agent服务（支持多轮工具调用）
                    result = await AgentService.run_agent(
                        model_config=model,
                        content=test_case.prompt,
                        system_prompt=test_case.system_prompt,
                        params=params,
                        tools=tools,
                        tools_config=tools_config,
                        conversation_history=test_case.conversation_history,
                        use_mock=use_mock,
                        max_iterations=5
                    )
                else:
                    # 使用原有的单次调用（无工具）
                    result = await LLMService.call_model(
                        model_config=model,
                        content=test_case.prompt,
                        system_prompt=test_case.system_prompt,
                        params=params,
                        tools=None,
                        stream=False,
                        conversation_history=test_case.conversation_history
                    )
                
                # 评估结果
                score = None
                if result.get("status") == "success":
                    # 从tool_call_history提取工具调用（如果有）
                    tool_calls_for_eval = None
                    if result.get("tool_call_history"):
                        # 转换为评估服务期望的格式
                        tool_calls_for_eval = [
                            {
                                "function": {
                                    "name": tc["tool_name"],
                                    "arguments": tc["arguments"]
                                }
                            }
                            for tc in result.get("tool_call_history", [])
                        ]
                    
                    score, eval_details = EvaluationService.evaluate_result(
                        output=result.get("output", ""),
                        expected_output=test_case.expected_output,
                        tool_calls=tool_calls_for_eval or result.get("tool_calls"),
                        expected_tool_calls=test_case.expected_tool_calls,
                        evaluation_criteria=test_case.evaluation_criteria,
                        evaluation_weights=test_case.evaluation_weights,
                        conversation_history=result.get("conversation_history"),
                        tool_call_history=result.get("tool_call_history")
                    )
                    # 将评估详情添加到metrics中
                    metrics = result.get("metrics", {})
                    metrics['evaluation'] = eval_details
                else:
                    metrics = result.get("metrics", {})
                
                # 保存结果到数据库
                db_result = TestResultDB(
                    test_case_id=test_case.id,
                    model_id=model.id,
                    output=result.get("output", ""),
                    metrics=metrics,
                    score=score,
                    status=result.get("status", "success"),
                    error_message=result.get("error_message")
                )
                db.add(db_result)
                
                results.append({
                    "test_case_id": test_case.id,
                    "model_id": model.id,
                    "status": result.get("status"),
                    "metrics": result.get("metrics")
                })
        
        db.commit()
        
        # 保存批次结果到JSON文件
        result_file = settings.RESULTS_DIR / f"{batch_id}.json"
        with open(result_file, 'w', encoding='utf-8') as f:
            json.dump({
                "batch_id": batch_id,
                "timestamp": datetime.now().isoformat(),
                "models": [{"id": m.id, "name": m.name} for m in models],
                "test_cases": [{"id": tc.id, "title": tc.title} for tc in test_cases],
                "results": results
            }, f, ensure_ascii=False, indent=2)
        
    except Exception as e:
        print(f"Error in batch test: {e}")
    finally:
        db.close()


@router.get("/results/{batch_id}")
async def get_batch_results(batch_id: str):
    """获取批次测试结果"""
    result_file = settings.RESULTS_DIR / f"{batch_id}.json"
    
    if not result_file.exists():
        raise HTTPException(status_code=404, detail="Batch results not found")
    
    with open(result_file, 'r', encoding='utf-8') as f:
        results = json.load(f)
    
    return results


@router.get("/compare", response_model=List[CompareResult])
async def compare_results(
    model_ids: str,  # 逗号分隔的模型ID
    test_case_ids: str,  # 逗号分隔的测试用例ID
    db: Session = Depends(get_db)
):
    """多模型对比结果"""
    # 解析ID列表
    model_id_list = [int(id) for id in model_ids.split(',')]
    test_case_id_list = [int(id) for id in test_case_ids.split(',')]
    
    # 查询结果
    results = db.query(TestResultDB).filter(
        TestResultDB.model_id.in_(model_id_list),
        TestResultDB.test_case_id.in_(test_case_id_list)
    ).all()
    
    # 按测试用例分组
    compare_results = {}
    for result in results:
        if result.test_case_id not in compare_results:
            test_case = db.query(TestCaseDB).filter(TestCaseDB.id == result.test_case_id).first()
            compare_results[result.test_case_id] = {
                "test_case_id": result.test_case_id,
                "test_case_title": test_case.title if test_case else "Unknown",
                "test_case_prompt": test_case.prompt if test_case else "",
                "expected_output": test_case.expected_output if test_case else "",
                "expected_tool_calls": test_case.expected_tool_calls if test_case else None,
                "results": []
            }
        
        model = db.query(ModelConfigDB).filter(ModelConfigDB.id == result.model_id).first()
        compare_results[result.test_case_id]["results"].append({
            "result_id": result.id,  # 添加result_id用于删除
            "model_id": result.model_id,
            "model_name": model.name if model else "Unknown",
            "output": result.output,
            "metrics": result.metrics,
            "score": result.score,
            "status": result.status
        })
    
    return list(compare_results.values())


@router.delete("/results/{result_id}", status_code=204)
async def delete_test_result(
    result_id: int,
    db: Session = Depends(get_db)
):
    """删除单个测试结果"""
    result = db.query(TestResultDB).filter(TestResultDB.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Test result not found")
    
    db.delete(result)
    db.commit()
    return None


@router.delete("/results/batch/{batch_id}", status_code=204)
async def delete_batch_results(
    batch_id: str,
    db: Session = Depends(get_db)
):
    """删除整个批次的测试结果"""
    # 删除JSON文件
    result_file = settings.RESULTS_DIR / f"{batch_id}.json"
    if result_file.exists():
        result_file.unlink()
    
    # 也可以从数据库中删除相关结果（如果有存储）
    # 这里简单处理，只删除文件
    return None


@router.get("/history")
async def get_batch_history():
    """获取所有批量测试历史记录"""
    import os
    from pathlib import Path
    
    results_dir = settings.RESULTS_DIR
    if not results_dir.exists():
        return []
    
    history = []
    for file in sorted(results_dir.glob("batch_*.json"), reverse=True):
        try:
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                history.append({
                    "batch_id": data.get("batch_id"),
                    "timestamp": data.get("timestamp"),
                    "models": data.get("models", []),
                    "test_cases": data.get("test_cases", []),
                    "total_tests": len(data.get("models", [])) * len(data.get("test_cases", []))
                })
        except Exception as e:
            print(f"Error reading batch file {file}: {e}")
            continue
    
    return history
