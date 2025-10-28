"""调试API - 单次对话测试"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Union
import json

from app.utils.database import get_db
from app.models.model_config import ModelConfigDB
from app.models.tool_definition import ToolDefinitionDB
from app.services.llm_service import LLMService

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
    stream: bool = Field(False, description="是否使用流式输出")


class ChatResponse(BaseModel):
    """聊天响应"""
    output: str
    metrics: Dict[str, Any]
    status: str
    error_message: Optional[str] = None
    tool_calls: Optional[list[Dict[str, Any]]] = None  # 添加工具调用信息


@router.post("/chat")
async def debug_chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    """单次对话测试，支持流式和非流式"""
    # 获取模型配置
    model_config = db.query(ModelConfigDB).filter(ModelConfigDB.id == request.model_id).first()
    if not model_config:
        raise HTTPException(status_code=404, detail="Model not found")

    # 加载工具定义
    tools = None
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

    # 加载工具定义
    tools = None
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

    # 统一处理content数组，直接传递给LLMService
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
    result = await LLMService.call_model(
        model_config=model_config,
        content=request.content,
        system_prompt=request.system_prompt,
        params=request.params,
        tools=tools,
        conversation_history=request.conversation_history,
        stream=False
    )
    return ChatResponse(
        output=result.get("output", ""),
        metrics=result.get("metrics", {}),
        status=result.get("status", "success"),
        error_message=result.get("error_message"),
        tool_calls=result.get("tool_calls")
    )
