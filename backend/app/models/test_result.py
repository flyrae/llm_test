"""测试结果数据模型"""
from sqlalchemy import Column, Integer, String, Text, DateTime, JSON, Float, ForeignKey
from sqlalchemy.sql import func
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime

from app.utils.database import Base


# SQLAlchemy ORM模型
class TestResultDB(Base):
    """测试结果数据库模型"""
    __tablename__ = "test_results"
    
    id = Column(Integer, primary_key=True, index=True)
    test_case_id = Column(Integer, ForeignKey("test_cases.id"), nullable=False)
    model_id = Column(Integer, ForeignKey("models.id"), nullable=False)
    output = Column(Text, nullable=False)
    metrics = Column(JSON)  # 性能指标
    score = Column(Float)  # 评分
    status = Column(String(20))  # success, error, timeout
    error_message = Column(Text)
    executed_at = Column(DateTime, default=func.now())


# Pydantic模型
class TestMetrics(BaseModel):
    """测试指标"""
    response_time: float = Field(..., description="响应时间(秒)")
    prompt_tokens: int = Field(..., description="输入token数")
    completion_tokens: int = Field(..., description="输出token数")
    total_tokens: int = Field(..., description="总token数")
    estimated_cost: Optional[float] = Field(None, description="估算成本(USD)")


class TestResultCreate(BaseModel):
    """创建测试结果"""
    test_case_id: int
    model_id: int
    output: str
    metrics: TestMetrics
    score: Optional[float] = None
    status: str = "success"
    error_message: Optional[str] = None


class TestResultResponse(BaseModel):
    """测试结果响应"""
    id: int
    test_case_id: int
    model_id: int
    output: str
    metrics: Dict[str, Any]
    score: Optional[float]
    status: str
    error_message: Optional[str]
    executed_at: datetime
    
    model_config = {"from_attributes": True}
