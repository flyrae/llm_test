#!/usr/bin/env python3
"""
初始化预设模型模板的脚本
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import get_database_url
from app.models.model_template import ModelTemplateDB
from app.config.model_presets import PRESET_TEMPLATES

def init_preset_templates():
    """初始化预设模板"""
    engine = create_engine(get_database_url())
    SessionLocal = sessionmaker(bind=engine)
    
    with SessionLocal() as db:
        for template_data in PRESET_TEMPLATES:
            # 检查是否已存在
            existing = db.query(ModelTemplateDB).filter(
                ModelTemplateDB.name == template_data["name"]
            ).first()
            
            if existing:
                print(f"⚠️  模板 '{template_data['name']}' 已存在，跳过...")
                continue
            
            # 创建新模板
            db_template = ModelTemplateDB(
                name=template_data["name"],
                provider=template_data["provider"],
                api_endpoint=template_data["api_endpoint"],
                available_models=template_data["available_models"],
                default_params=template_data["default_params"],
                description=template_data["description"]
            )
            
            db.add(db_template)
            print(f"✅ 添加模板: {template_data['name']}")
        
        db.commit()
        print("\n🎉 预设模板初始化完成！")

if __name__ == "__main__":
    init_preset_templates()