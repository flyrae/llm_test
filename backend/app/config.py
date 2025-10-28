"""应用配置管理"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """应用配置"""
    
    # 应用基础配置
    APP_NAME: str = "LLM Test Tool"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务器配置
    HOST: str = "0.0.0.0"
    PORT: int = 8008
    
    # 数据库配置
    BASE_DIR: Path = Path(__file__).parent.parent
    DATA_DIR: Path = BASE_DIR / "data"
    DATABASE_URL: str = f"sqlite:///{DATA_DIR}/models.db"
    RESULTS_DIR: Path = DATA_DIR / "results"
    
    # CORS配置
    CORS_ORIGINS: list = ["http://localhost:8000", "http://127.0.0.1:8000"]
    
    # API密钥加密
    ENCRYPTION_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 确保数据目录存在
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.RESULTS_DIR.mkdir(parents=True, exist_ok=True)


# 全局配置实例
settings = Settings()
