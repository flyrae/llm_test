#!/usr/bin/env python3
"""
添加模型模板表的数据库迁移脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine, text
from app.config import get_database_url

def migrate_add_model_templates():
    """添加模型模板表"""
    engine = create_engine(get_database_url())
    
    with engine.connect() as conn:
        # 创建模型模板表
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS model_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL UNIQUE,
                provider VARCHAR(50) NOT NULL,
                api_endpoint VARCHAR(500) NOT NULL,
                available_models JSON NOT NULL,
                default_params JSON,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """))
        
        conn.commit()
        print("✅ 模型模板表创建成功")

if __name__ == "__main__":
    migrate_add_model_templates()