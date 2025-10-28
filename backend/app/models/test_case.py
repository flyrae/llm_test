"""测试用例数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime

from app.utils.database import Base


# SQLAlchemy ORM模型
class TestCaseDB(Base):
    """测试用例数据库模型"""
    __tablename__ = "test_cases"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    category = Column(String(50))
    prompt = Column(Text, nullable=False)
    system_prompt = Column(Text)  # 系统提示词
    conversation_history = Column(JSON)  # 多轮对话历史 [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}]
    expected_output = Column(Text)
    evaluation_criteria = Column(JSON)  # 评估标准
    tools = Column(JSON)  # 关联的工具ID列表
    expected_tool_calls = Column(JSON)  # 期望的工具调用（用于评估）
    evaluation_weights = Column(JSON)  # 评分权重配置 {tool_calls: 70, text_similarity: 20, custom_criteria: 10}
    tags = Column(String(200))
    meta_data = Column(JSON)  # 其他元数据
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


# Pydantic模型
class TestCaseCreate(BaseModel):
    """创建测试用例"""
    title: str = Field(..., min_length=1, max_length=200)
    category: Optional[str] = None
    prompt: str = Field(..., min_length=1)
    system_prompt: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None  # 多轮对话历史（支持tool_calls）
    expected_output: Optional[str] = None
    evaluation_criteria: Optional[Dict[str, Any]] = None
    tools: Optional[List[int]] = None  # 关联的工具ID列表
    expected_tool_calls: Optional[List[Dict[str, Any]]] = None  # 期望的工具调用
    evaluation_weights: Optional[Dict[str, int]] = None  # 评分权重配置
    tags: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class TestCaseUpdate(BaseModel):
    """更新测试用例"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[str] = None
    prompt: Optional[str] = None
    system_prompt: Optional[str] = None
    conversation_history: Optional[List[Dict[str, Any]]] = None  # 多轮对话历史（支持tool_calls）
    expected_output: Optional[str] = None
    evaluation_criteria: Optional[Dict[str, Any]] = None
    tools: Optional[List[int]] = None  # 关联的工具ID列表
    expected_tool_calls: Optional[List[Dict[str, Any]]] = None  # 期望的工具调用
    evaluation_weights: Optional[Dict[str, int]] = None  # 评分权重配置
    tags: Optional[str] = None
    meta_data: Optional[Dict[str, Any]] = None


class TestCaseResponse(BaseModel):
    """测试用例响应"""
    id: int
    title: str
    category: Optional[str]
    prompt: str
    system_prompt: Optional[str]
    conversation_history: Optional[List[Dict[str, Any]]]  # 多轮对话历史（支持tool_calls）
    expected_output: Optional[str]
    evaluation_criteria: Optional[Dict[str, Any]]
    tools: Optional[List[int]]  # 关联的工具ID列表
    expected_tool_calls: Optional[List[Dict[str, Any]]]  # 期望的工具调用
    evaluation_weights: Optional[Dict[str, int]]  # 评分权重配置
    tags: Optional[str]
    meta_data: Optional[Dict[str, Any]]
    created_at: datetime
    updated_at: datetime
    
    model_config = {"from_attributes": True}


class TestCaseImport(BaseModel):
    """批量导入测试用例"""
    test_cases: List[TestCaseCreate]
