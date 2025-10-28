"""模型模板数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.utils.database import Base


# SQLAlchemy ORM模型
class ModelTemplateDB(Base):
    """模型模板数据库模型"""
    __tablename__ = "model_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    provider = Column(String(50), nullable=False)
    api_endpoint = Column(String(500), nullable=False)
    available_models = Column(JSON)  # 可用的模型列表
    default_params = Column(JSON)  # 默认参数模板
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Pydantic模型
class ModelInfo(BaseModel):
    """模型信息"""
    model_name: str = Field(..., description="模型名称")
    display_name: str = Field(..., description="显示名称")
    description: Optional[str] = Field(None, description="模型描述")
    default_params: Optional[Dict[str, Any]] = Field(None, description="模型特定参数")


class ModelTemplateCreate(BaseModel):
    """创建模型模板"""
    name: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(..., pattern="^(openai|anthropic|local|custom)$")
    api_endpoint: str = Field(..., min_length=1)
    available_models: List[ModelInfo] = Field(..., min_items=1)
    default_params: Optional[Dict[str, Any]] = None
    description: Optional[str] = None


class ModelTemplateUpdate(BaseModel):
    """更新模型模板"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = Field(None, pattern="^(openai|anthropic|local|custom)$")
    api_endpoint: Optional[str] = None
    available_models: Optional[List[ModelInfo]] = None
    default_params: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    is_active: Optional[bool] = None


class ModelTemplateResponse(BaseModel):
    """模型模板响应"""
    model_config = {"from_attributes": True}
    
    id: int
    name: str
    provider: str
    api_endpoint: str
    available_models: List[Dict[str, Any]]
    default_params: Dict[str, Any]
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class BatchCreateModelsRequest(BaseModel):
    """批量创建模型请求"""
    template_id: int = Field(..., description="模板ID")
    models: List[str] = Field(..., min_items=1, description="要创建的模型名称列表")
    api_key: Optional[str] = Field(None, description="API密钥")
    name_prefix: Optional[str] = Field(None, description="模型名称前缀")
    tags: Optional[str] = Field(None, description="标签")


class BatchCreateModelsResponse(BaseModel):
    """批量创建模型响应"""
    created_count: int
    failed_count: int
    created_models: List[Dict[str, Any]]
    errors: List[str]