"""模型配置管理API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utils.database import get_db
from app.models.model_config import (
    ModelConfigDB, ModelConfigCreate, ModelConfigUpdate, ModelConfigResponse
)
from app.utils.validators import validate_api_endpoint, encrypt_api_key

router = APIRouter()


@router.get("/", response_model=List[ModelConfigResponse])
async def list_models(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """获取模型列表"""
    models = db.query(ModelConfigDB).offset(skip).limit(limit).all()
    return models


@router.get("/{model_id}", response_model=ModelConfigResponse)
async def get_model(model_id: int, db: Session = Depends(get_db)):
    """获取单个模型配置"""
    model = db.query(ModelConfigDB).filter(ModelConfigDB.id == model_id).first()
    if not model:
        raise HTTPException(status_code=404, detail="Model not found")
    return model


@router.post("/", response_model=ModelConfigResponse, status_code=status.HTTP_201_CREATED)
async def create_model(
    model_config: ModelConfigCreate,
    db: Session = Depends(get_db)
):
    """创建模型配置"""
    # 验证API端点
    if model_config.api_endpoint and not validate_api_endpoint(model_config.api_endpoint):
        raise HTTPException(status_code=400, detail="Invalid API endpoint")
    
    # 检查名称是否已存在
    existing = db.query(ModelConfigDB).filter(ModelConfigDB.name == model_config.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Model name already exists")
    
    # 加密API密钥
    encrypted_key = None
    if model_config.api_key:
        encrypted_key = encrypt_api_key(model_config.api_key)
    
    # 创建数据库记录
    db_model = ModelConfigDB(
        name=model_config.name,
        provider=model_config.provider,
        api_endpoint=model_config.api_endpoint,
        api_key=encrypted_key,
        model_name=model_config.model_name,
        default_params=model_config.default_params or {},
        tags=model_config.tags,
        description=model_config.description
    )
    
    db.add(db_model)
    db.commit()
    db.refresh(db_model)
    return db_model


@router.put("/{model_id}", response_model=ModelConfigResponse)
async def update_model(
    model_id: int,
    model_config: ModelConfigUpdate,
    db: Session = Depends(get_db)
):
    """更新模型配置"""
    db_model = db.query(ModelConfigDB).filter(ModelConfigDB.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    # 更新字段
    update_data = model_config.model_dump(exclude_unset=True)
    
    # 验证API端点
    if "api_endpoint" in update_data and update_data["api_endpoint"]:
        if not validate_api_endpoint(update_data["api_endpoint"]):
            raise HTTPException(status_code=400, detail="Invalid API endpoint")
    
    # 加密API密钥
    if "api_key" in update_data and update_data["api_key"]:
        update_data["api_key"] = encrypt_api_key(update_data["api_key"])
    
    # default_params已经是字典，不需要额外处理
    
    for key, value in update_data.items():
        setattr(db_model, key, value)
    
    db.commit()
    db.refresh(db_model)
    return db_model


@router.delete("/{model_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_model(model_id: int, db: Session = Depends(get_db)):
    """删除模型配置"""
    db_model = db.query(ModelConfigDB).filter(ModelConfigDB.id == model_id).first()
    if not db_model:
        raise HTTPException(status_code=404, detail="Model not found")
    
    db.delete(db_model)
    db.commit()
    return None
