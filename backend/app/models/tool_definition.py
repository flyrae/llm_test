"""工具定义数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.utils.database import Base


# SQLAlchemy ORM模型
class ToolDefinitionDB(Base):
    """工具定义数据库模型"""
    __tablename__ = "tool_definitions"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    parameters = Column(JSON, nullable=False)  # JSON Schema格式的参数定义
    category = Column(String(50))  # 工具分类：web, file, math, custom等
    example_call = Column(JSON)  # 示例调用
    mock_responses = Column(JSON)  # 模拟响应配置
    tags = Column(String(200))
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Pydantic模型
class ToolParameter(BaseModel):
    """工具参数定义"""
    type: str = Field(..., description="参数类型：string, number, boolean, array, object")
    description: str = Field(..., description="参数描述")
    enum: Optional[List[Any]] = Field(None, description="枚举值")
    items: Optional[Dict[str, Any]] = Field(None, description="数组项定义")
    properties: Optional[Dict[str, Any]] = Field(None, description="对象属性定义")


class ToolParameters(BaseModel):
    """工具参数Schema"""
    type: str = Field(default="object", description="参数类型")
    properties: Dict[str, Dict[str, Any]] = Field(default_factory=dict, description="参数属性定义")
    required: List[str] = Field(default_factory=list, description="必需参数列表")


class ToolDefinitionCreate(BaseModel):
    """创建工具定义"""
    model_config = {"extra": "ignore"}  # 忽略额外的字段（如 results）
    
    name: str = Field(..., min_length=1, max_length=100, description="工具名称")
    description: str = Field(..., min_length=1, description="工具描述")
    parameters: Optional[ToolParameters] = Field(
        default=None,
        description="参数定义，如果为空则使用默认的空参数对象"
    )
    category: Optional[str] = Field(None, description="工具分类")
    example_call: Optional[Dict[str, Any]] = Field(None, description="示例调用")
    mock_responses: Optional[Dict[str, Any]] = Field(None, description="模拟响应配置")
    tags: Optional[str] = Field(None, description="标签")
    
    @field_validator('parameters', mode='before')
    @classmethod
    def validate_parameters(cls, v):
        """处理空的parameters对象"""
        if v is None or v == {}:
            # 返回默认的空参数对象
            return ToolParameters(type="object", properties={}, required=[])
        return v


class ToolDefinitionUpdate(BaseModel):
    """更新工具定义"""
    model_config = {"extra": "ignore"}  # 忽略额外的字段
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    parameters: Optional[ToolParameters] = None
    category: Optional[str] = None
    example_call: Optional[Dict[str, Any]] = None
    mock_responses: Optional[Dict[str, Any]] = None
    tags: Optional[str] = None


class ToolDefinitionResponse(BaseModel):
    """工具定义响应"""
    id: int
    name: str
    description: str
    parameters: Dict[str, Any]
    category: Optional[str]
    example_call: Optional[Dict[str, Any]]
    mock_responses: Optional[Dict[str, Any]]
    tags: Optional[str]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class ToolCallExample(BaseModel):
    """工具调用示例（用于文档）"""
    function_name: str
    arguments: Dict[str, Any]
    expected_behavior: str
