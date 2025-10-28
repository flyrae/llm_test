"""系统提示词数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.utils.database import Base


# SQLAlchemy ORM模型
class SystemPromptDB(Base):
    """系统提示词数据库模型"""
    __tablename__ = "system_prompts"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    content = Column(Text, nullable=False)
    category = Column(String(50))  # 分类：通用、编程、翻译、写作等
    description = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Pydantic模型（API数据传输）
class SystemPromptCreate(BaseModel):
    """创建系统提示词"""
    name: str = Field(..., min_length=1, max_length=100, description="提示词名称")
    content: str = Field(..., min_length=1, description="提示词内容")
    category: Optional[str] = Field(None, max_length=50, description="分类")
    description: Optional[str] = Field(None, description="描述")


class SystemPromptUpdate(BaseModel):
    """更新系统提示词"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    content: Optional[str] = Field(None, min_length=1)
    category: Optional[str] = Field(None, max_length=50)
    description: Optional[str] = None


class SystemPromptResponse(BaseModel):
    """系统提示词响应"""
    model_config = {"from_attributes": True}
    
    id: int
    name: str
    content: str
    category: Optional[str]
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
