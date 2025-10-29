"""Pydantic models for tool mock generation via LLM"""
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class MockScenario(BaseModel):
    """Scenario hint that guides mock generation."""

    title: str = Field(..., description="简短的场景名称")
    type: str = Field(
        default="success", description="场景类型：success 或 error，大小写敏感"
    )
    arguments: Dict[str, Any] = Field(
        default_factory=dict, description="调用该工具时使用的参数示例"
    )
    expected_behavior: Optional[str] = Field(
        None, description="该场景下工具应当呈现的行为或结果概述"
    )
    expected_response: Optional[Dict[str, Any]] = Field(
        None, description="期望的工具返回结构示例，可为空"
    )


class ToolMockGenerationRequest(BaseModel):
    """请求使用大模型生成工具 mock 配置."""

    model_id: int = Field(..., description="用于生成的模型配置 ID")
    language: Optional[str] = Field(
        default="zh", description="输出语言偏好，例如 zh 或 en"
    )
    prompt: Optional[str] = Field(
        None, description="附加的自定义说明，影响生成内容风格"
    )
    response_type: Optional[str] = Field(
        default="template", description="期望生成的 mock 响应类型"
    )
    include_error_scenarios: bool = Field(
        default=True, description="是否要求生成错误场景配置"
    )
    scenarios: List[MockScenario] = Field(
        default_factory=list, description="用于指导生成的典型调用场景集合"
    )
    persist: bool = Field(
        default=False, description="是否将生成结果写回数据库"
    )
    overwrite: bool = Field(
        default=False, description="存在 mock 配置时是否允许覆盖"
    )


class ToolMockGenerationResponse(BaseModel):
    """mock 数据生成结果."""

    status: str = Field(..., description="生成状态：success、error、invalid_output 等")
    mock_config: Optional[Dict[str, Any]] = Field(
        None, description="生成的 mock 配置，如成功则返回"
    )
    validation_error: Optional[str] = Field(
        None, description="mock 配置校验失败时的错误信息"
    )
    raw_output: Optional[str] = Field(
        None, description="模型原始输出，便于调试"
    )
    metrics: Optional[Dict[str, Any]] = Field(
        None, description="调用大模型的性能指标"
    )
    saved: bool = Field(default=False, description="是否已将配置写入数据库")
