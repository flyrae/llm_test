"""模型配置数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from app.utils.database import Base


# SQLAlchemy ORM模型
class ModelConfigDB(Base):
    """模型配置数据库模型"""
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    provider = Column(String(50), nullable=False)  # openai, anthropic, local, custom
    api_endpoint = Column(String(500))
    api_key = Column(Text)  # 加密存储
    model_name = Column(String(100), nullable=False)
    default_params = Column(JSON)  # temperature, top_p, max_tokens等
    tags = Column(String(200))
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Pydantic模型（API数据传输）
class ModelParams(BaseModel):
    """模型默认参数"""
    model_config = {"protected_namespaces": ()}
    
    temperature: float = Field(default=0.7, ge=0, le=2)
    top_p: float = Field(default=1.0, ge=0, le=1)
    max_tokens: Optional[int] = Field(default=1000, ge=1)
    frequency_penalty: float = Field(default=0, ge=-2, le=2)
    presence_penalty: float = Field(default=0, ge=-2, le=2)


class ModelConfigCreate(BaseModel):
    """创建模型配置"""
    model_config = {"protected_namespaces": ()}
    
    name: str = Field(..., min_length=1, max_length=100)
    provider: str = Field(..., pattern="^(openai|anthropic|local|custom)$")
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    model_name: str = Field(..., min_length=1)
    default_params: Optional[Dict[str, Any]] = None
    tags: Optional[str] = None
    description: Optional[str] = None


class ModelConfigUpdate(BaseModel):
    """更新模型配置"""
    model_config = {"protected_namespaces": ()}
    
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    provider: Optional[str] = Field(None, pattern="^(openai|anthropic|local|custom)$")
    api_endpoint: Optional[str] = None
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    default_params: Optional[Dict[str, Any]] = None
    tags: Optional[str] = None
    description: Optional[str] = None


class ModelConfigResponse(BaseModel):
    """模型配置响应"""
    model_config = {"protected_namespaces": (), "from_attributes": True}
    
    id: int
    name: str
    provider: str
    api_endpoint: Optional[str]
    model_name: str
    default_params: Dict[str, Any]
    tags: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
