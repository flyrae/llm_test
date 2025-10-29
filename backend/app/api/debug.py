"""调试API - 单次对话测试"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union, List
import json

from app.utils.database import get_db
from app.models.model_config import ModelConfigDB
from app.models.tool_definition import ToolDefinitionDB
from app.services.llm_service import LLMService
from app.services.mock_tool_executor import MockToolExecutor
from app.services.agent_service import AgentService

router = APIRouter()


class ChatRequest(BaseModel):
    """聊天请求"""
    model_config = {"protected_namespaces": ()}
    
    model_id: int = Field(..., description="模型ID")
    content: Union[str, list] = Field(..., description="用户消息内容：字符串（纯文本）或数组（支持text/image_url）")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    params: Optional[Dict[str, Any]] = Field(None, description="模型参数")
    tool_ids: Optional[list[int]] = Field(None, description="工具ID列表")
    conversation_history: Optional[list[Dict[str, Any]]] = Field(None, description="对话历史（支持tool_calls）")
    use_mock: bool = Field(False, description="是否使用模拟工具执行")
    use_agent: bool = Field(True, description="是否使用Agent模式（支持多轮工具调用）")
    max_iterations: int = Field(5, description="Agent最大迭代次数")
    stream: bool = Field(False, description="是否使用流式输出")


class ChatResponse(BaseModel):
    """聊天响应"""
    output: str
    metrics: Dict[str, Any]
    status: str
    error_message: Optional[str] = None
    tool_calls: Optional[list[Dict[str, Any]]] = None  # 首次工具调用信息（兼容）
    tool_call_history: Optional[List[Dict[str, Any]]] = None  # 完整的工具调用历史
    conversation_history: Optional[List[Dict[str, Any]]] = None  # 完整的对话历史
    mock_tool_results: Optional[list[Dict[str, Any]]] = None  # 已废弃，保留兼容性


@router.post("/chat")
async def debug_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """单次对话测试，支持流式和非流式，支持Agent多轮工具调用"""
    # 获取模型配置
    model_config = db.query(ModelConfigDB).filter(ModelConfigDB.id == request.model_id).first()
    if not model_config:
        raise HTTPException(status_code=404, detail="Model not found")

    # 加载工具定义
    tools = None
    tool_definitions_dict = {}  # 用于mock执行
    if request.tool_ids:
        tool_definitions = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.id.in_(request.tool_ids)).all()
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
        # 构建工具配置字典
        tool_definitions_dict = {tool.name: tool.mock_responses for tool in tool_definitions}

    # 流式模式暂不支持Agent（需要等待工具执行完成）
    if request.stream:
        async def event_generator():
            try:
                stream_result = await LLMService.call_model(
                    model_config=model_config,
                    content=request.content,
                    system_prompt=request.system_prompt,
                    params=request.params,
                    tools=tools,
                    conversation_history=request.conversation_history,
                    stream=True
                )
                async for chunk in stream_result:
                    yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                yield f"data: {json.dumps({'error': str(e), 'done': True, 'status': 'error'})}\n\n"
        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no"
            }
        )
    
    # 非流式模式
    # 如果启用Agent模式且有工具，使用Agent服务
    if request.use_agent and tools:
        result = await AgentService.run_agent(
            model_config=model_config,
            content=request.content,
            system_prompt=request.system_prompt,
            params=request.params,
            tools=tools,
            tools_config=tool_definitions_dict,
            conversation_history=request.conversation_history,
            use_mock=request.use_mock,
            max_iterations=request.max_iterations
        )
        
        # Agent返回完整的工具调用历史
        return ChatResponse(
            output=result.get("output", ""),
            metrics=result.get("metrics", {}),
            status=result.get("status", "success"),
            error_message=result.get("error_message"),
            tool_calls=result.get("tool_call_history", [])[:1] if result.get("tool_call_history") else None,  # 兼容旧接口
            tool_call_history=result.get("tool_call_history", []),
            conversation_history=result.get("conversation_history", [])
        )
    else:
        # 原有的单次调用逻辑（兼容旧版本）
        result = await LLMService.call_model(
            model_config=model_config,
            content=request.content,
            system_prompt=request.system_prompt,
            params=request.params,
            tools=tools,
            conversation_history=request.conversation_history,
            stream=False
        )
        
        # 如果启用了mock模式且有工具调用，执行模拟工具调用（旧逻辑，仅用于兼容）
        if request.use_mock and result.get("tool_calls"):
            tool_calls = result.get("tool_calls", [])
            mock_results = MockToolExecutor.execute_multiple_tool_calls(
                tool_calls, tool_definitions_dict
            )
            result["mock_tool_results"] = mock_results
        
        return ChatResponse(
            output=result.get("output", ""),
            metrics=result.get("metrics", {}),
            status=result.get("status", "success"),
            error_message=result.get("error_message"),
            tool_calls=result.get("tool_calls"),
            mock_tool_results=result.get("mock_tool_results")
        )
