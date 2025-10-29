"""训练数据生成和导出API"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import json
import io
from datetime import datetime

from app.utils.database import get_db
from app.models.test_case import TestCaseDB
from app.models.tool_definition import ToolDefinitionDB
from app.models.model_config import ModelConfigDB
from app.services.llm_service import LLMService
from app.services.mock_tool_executor import MockToolExecutor

router = APIRouter()


class TrainingDataRequest(BaseModel):
    """训练数据生成请求"""
    test_case_ids: List[int] = Field(..., description="测试用例ID列表")
    model_id: int = Field(..., description="使用的模型ID")
    format: str = Field("openai", description="导出格式：openai, anthropic, jsonl, csv")
    include_mock_results: bool = Field(True, description="是否包含模拟工具执行结果")


class TrainingSample(BaseModel):
    """训练样本"""
    messages: List[Dict[str, Any]]
    tools: Optional[List[Dict[str, Any]]] = None
    tool_results: Optional[List[Dict[str, Any]]] = None


@router.post("/generate")
async def generate_training_data(
    request: TrainingDataRequest,
    db: Session = Depends(get_db)
):
    """
    生成训练数据
    
    批量执行测试用例，收集完整的对话链路（包含工具调用和模拟结果），
    生成用于Agent训练的数据集
    """
    # 获取模型配置
    model_config = db.query(ModelConfigDB).filter(ModelConfigDB.id == request.model_id).first()
    if not model_config:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # 获取测试用例
    test_cases = db.query(TestCaseDB).filter(TestCaseDB.id.in_(request.test_case_ids)).all()
    if not test_cases:
        raise HTTPException(status_code=404, detail="No test cases found")
    
    training_samples = []
    
    for test_case in test_cases:
        try:
            # 构建消息列表
            messages = []
            
            # 添加系统消息
            if test_case.system_prompt:
                messages.append({
                    "role": "system",
                    "content": test_case.system_prompt
                })
            
            # 添加对话历史
            if test_case.conversation_history:
                messages.extend(test_case.conversation_history)
            
            # 添加用户提示
            messages.append({
                "role": "user",
                "content": test_case.prompt
            })
            
            # 加载工具定义
            tools = None
            tool_definitions_dict = {}
            if test_case.tools:
                tool_definitions = db.query(ToolDefinitionDB).filter(
                    ToolDefinitionDB.id.in_(test_case.tools)
                ).all()
                
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
                
                tool_definitions_dict = {
                    tool.name: tool.mock_responses for tool in tool_definitions
                }
            
            # 调用LLM获取响应
            result = await LLMService.call_model(
                model_config=model_config,
                content=test_case.prompt,
                system_prompt=test_case.system_prompt,
                params=None,
                tools=tools,
                conversation_history=test_case.conversation_history,
                stream=False
            )
            
            # 添加助手响应
            assistant_message = {
                "role": "assistant",
                "content": result.get("output", "")
            }
            
            # 如果有工具调用
            tool_results = None
            if result.get("tool_calls"):
                assistant_message["tool_calls"] = result["tool_calls"]
                messages.append(assistant_message)
                
                # 如果需要模拟工具执行
                if request.include_mock_results and (test_case.use_mock or True):
                    mock_results = MockToolExecutor.execute_multiple_tool_calls(
                        result["tool_calls"],
                        tool_definitions_dict
                    )
                    
                    # 添加工具结果到消息中
                    for mock_result in mock_results:
                        messages.append({
                            "role": "tool",
                            "tool_call_id": mock_result.get("tool_call_id"),
                            "content": json.dumps(mock_result.get("result"), ensure_ascii=False)
                        })
                    
                    tool_results = mock_results
            else:
                messages.append(assistant_message)
            
            # 创建训练样本
            sample = {
                "test_case_id": test_case.id,
                "test_case_title": test_case.title,
                "messages": messages,
                "tools": tools,
                "tool_results": tool_results,
                "expected_output": test_case.expected_output,
                "expected_tool_calls": test_case.expected_tool_calls,
                "timestamp": datetime.now().isoformat()
            }
            
            training_samples.append(sample)
            
        except Exception as e:
            # 记录错误但继续处理其他用例
            training_samples.append({
                "test_case_id": test_case.id,
                "test_case_title": test_case.title,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            })
    
    return {
        "total": len(training_samples),
        "samples": training_samples,
        "model_id": request.model_id,
        "model_name": model_config.name,
        "generated_at": datetime.now().isoformat()
    }


@router.post("/export")
async def export_training_data(
    request: TrainingDataRequest,
    db: Session = Depends(get_db)
):
    """
    导出训练数据为指定格式的文件
    
    支持格式：
    - openai: OpenAI fine-tuning格式 (JSONL)
    - anthropic: Anthropic格式
    - jsonl: 通用JSONL格式
    - csv: CSV格式（简化版）
    """
    # 生成训练数据
    training_data = await generate_training_data(request, db)
    
    if request.format == "openai":
        content = _export_openai_format(training_data)
        filename = f"training_data_openai_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        media_type = "application/x-ndjson"
    elif request.format == "anthropic":
        content = _export_anthropic_format(training_data)
        filename = f"training_data_anthropic_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        media_type = "application/x-ndjson"
    elif request.format == "jsonl":
        content = _export_jsonl_format(training_data)
        filename = f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jsonl"
        media_type = "application/x-ndjson"
    elif request.format == "csv":
        content = _export_csv_format(training_data)
        filename = f"training_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        media_type = "text/csv"
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported format: {request.format}")
    
    # 返回文件流
    return StreamingResponse(
        io.BytesIO(content.encode("utf-8")),
        media_type=media_type,
        headers={
            "Content-Disposition": f"attachment; filename={filename}"
        }
    )


def _export_openai_format(training_data: Dict[str, Any]) -> str:
    """导出为OpenAI fine-tuning格式"""
    lines = []
    for sample in training_data["samples"]:
        if "error" in sample:
            continue
        
        # OpenAI格式：{"messages": [...], "tools": [...]}
        line_data = {
            "messages": sample["messages"]
        }
        if sample.get("tools"):
            line_data["tools"] = sample["tools"]
        
        lines.append(json.dumps(line_data, ensure_ascii=False))
    
    return "\n".join(lines)


def _export_anthropic_format(training_data: Dict[str, Any]) -> str:
    """导出为Anthropic格式"""
    lines = []
    for sample in training_data["samples"]:
        if "error" in sample:
            continue
        
        # Anthropic格式类似，但可能需要调整
        line_data = {
            "messages": sample["messages"],
            "tools": sample.get("tools")
        }
        
        lines.append(json.dumps(line_data, ensure_ascii=False))
    
    return "\n".join(lines)


def _export_jsonl_format(training_data: Dict[str, Any]) -> str:
    """导出为通用JSONL格式（包含完整信息）"""
    lines = []
    for sample in training_data["samples"]:
        lines.append(json.dumps(sample, ensure_ascii=False))
    
    return "\n".join(lines)


def _export_csv_format(training_data: Dict[str, Any]) -> str:
    """导出为CSV格式（简化版）"""
    import csv
    from io import StringIO
    
    output = StringIO()
    writer = csv.writer(output)
    
    # 写入表头
    writer.writerow([
        "test_case_id",
        "test_case_title",
        "prompt",
        "expected_output",
        "has_tool_calls",
        "tool_count",
        "timestamp"
    ])
    
    # 写入数据
    for sample in training_data["samples"]:
        if "error" in sample:
            continue
        
        # 提取prompt
        prompt = ""
        for msg in sample["messages"]:
            if msg["role"] == "user":
                prompt = msg["content"]
                break
        
        writer.writerow([
            sample.get("test_case_id", ""),
            sample.get("test_case_title", ""),
            prompt,
            sample.get("expected_output", ""),
            "Yes" if sample.get("tool_results") else "No",
            len(sample.get("tool_results", [])),
            sample.get("timestamp", "")
        ])
    
    return output.getvalue()


@router.get("/stats")
async def get_training_stats(db: Session = Depends(get_db)):
    """获取训练数据统计信息"""
    total_test_cases = db.query(TestCaseDB).count()
    mock_enabled_cases = db.query(TestCaseDB).filter(TestCaseDB.use_mock == True).count()
    cases_with_tools = db.query(TestCaseDB).filter(TestCaseDB.tools != None).count()
    
    return {
        "total_test_cases": total_test_cases,
        "mock_enabled_cases": mock_enabled_cases,
        "cases_with_tools": cases_with_tools,
        "total_tools": db.query(ToolDefinitionDB).count(),
        "tools_with_mock": db.query(ToolDefinitionDB).filter(
            ToolDefinitionDB.mock_responses != None
        ).count()
    }
