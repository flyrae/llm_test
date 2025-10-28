"""模型模板管理API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.utils.database import get_db
from app.models.model_template import (
    ModelTemplateDB, ModelTemplateCreate, ModelTemplateUpdate, 
    ModelTemplateResponse, BatchCreateModelsRequest, BatchCreateModelsResponse
)
from app.models.model_config import ModelConfigDB
from app.utils.validators import validate_api_endpoint, encrypt_api_key

router = APIRouter()


@router.get("/", response_model=List[ModelTemplateResponse])
async def list_templates(
    skip: int = 0,
    limit: int = 100,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """获取模型模板列表"""
    query = db.query(ModelTemplateDB)
    if active_only:
        query = query.filter(ModelTemplateDB.is_active == True)
    templates = query.offset(skip).limit(limit).all()
    return templates


@router.get("/{template_id}", response_model=ModelTemplateResponse)
async def get_template(template_id: int, db: Session = Depends(get_db)):
    """获取单个模型模板"""
    template = db.query(ModelTemplateDB).filter(ModelTemplateDB.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("/", response_model=ModelTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template: ModelTemplateCreate,
    db: Session = Depends(get_db)
):
    """创建模型模板"""
    # 验证API端点
    if not validate_api_endpoint(template.api_endpoint):
        raise HTTPException(status_code=400, detail="Invalid API endpoint")
    
    # 检查名称是否已存在
    existing = db.query(ModelTemplateDB).filter(ModelTemplateDB.name == template.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Template name already exists")
    
    # 转换available_models为字典格式
    available_models = [model.model_dump() for model in template.available_models]
    
    # 创建数据库记录
    db_template = ModelTemplateDB(
        name=template.name,
        provider=template.provider,
        api_endpoint=template.api_endpoint,
        available_models=available_models,
        default_params=template.default_params or {},
        description=template.description
    )
    
    db.add(db_template)
    db.commit()
    db.refresh(db_template)
    return db_template


@router.put("/{template_id}", response_model=ModelTemplateResponse)
async def update_template(
    template_id: int,
    template: ModelTemplateUpdate,
    db: Session = Depends(get_db)
):
    """更新模型模板"""
    db_template = db.query(ModelTemplateDB).filter(ModelTemplateDB.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 更新字段
    update_data = template.model_dump(exclude_unset=True)
    
    # 验证API端点
    if "api_endpoint" in update_data and update_data["api_endpoint"]:
        if not validate_api_endpoint(update_data["api_endpoint"]):
            raise HTTPException(status_code=400, detail="Invalid API endpoint")
    
    # 转换available_models
    if "available_models" in update_data and update_data["available_models"]:
        update_data["available_models"] = [
            model.model_dump() if hasattr(model, 'model_dump') else model 
            for model in update_data["available_models"]
        ]
    
    for key, value in update_data.items():
        setattr(db_template, key, value)
    
    db.commit()
    db.refresh(db_template)
    return db_template


@router.delete("/{template_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(template_id: int, db: Session = Depends(get_db)):
    """删除模型模板"""
    db_template = db.query(ModelTemplateDB).filter(ModelTemplateDB.id == template_id).first()
    if not db_template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    db.delete(db_template)
    db.commit()
    return None


@router.post("/{template_id}/batch-create", response_model=BatchCreateModelsResponse)
async def batch_create_models(
    template_id: int,
    request: BatchCreateModelsRequest,
    db: Session = Depends(get_db)
):
    """从模板批量创建模型"""
    # 获取模板
    template = db.query(ModelTemplateDB).filter(ModelTemplateDB.id == template_id).first()
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    
    # 加密API密钥
    encrypted_key = None
    if request.api_key:
        encrypted_key = encrypt_api_key(request.api_key)
    
    created_models = []
    errors = []
    
    # 获取模板中可用的模型信息
    available_models_dict = {model["model_name"]: model for model in template.available_models}
    
    for model_name in request.models:
        try:
            # 检查模型是否在模板中定义
            if model_name not in available_models_dict:
                errors.append(f"Model '{model_name}' not found in template")
                continue
            
            model_info = available_models_dict[model_name]
            
            # 生成模型配置名称
            config_name = f"{request.name_prefix or template.name}_{model_info.get('display_name', model_name)}"
            
            # 检查名称是否已存在
            existing = db.query(ModelConfigDB).filter(ModelConfigDB.name == config_name).first()
            if existing:
                errors.append(f"Model name '{config_name}' already exists")
                continue
            
            # 合并默认参数
            merged_params = {**template.default_params}
            if model_info.get("default_params"):
                merged_params.update(model_info["default_params"])
            
            # 创建模型配置
            db_model = ModelConfigDB(
                name=config_name,
                provider=template.provider,
                api_endpoint=template.api_endpoint,
                api_key=encrypted_key,
                model_name=model_name,
                default_params=merged_params,
                tags=request.tags,
                description=model_info.get("description", f"Auto-created from template: {template.name}")
            )
            
            db.add(db_model)
            db.flush()  # 获取ID但不提交
            
            created_models.append({
                "id": db_model.id,
                "name": db_model.name,
                "model_name": db_model.model_name,
                "provider": db_model.provider
            })
            
        except Exception as e:
            errors.append(f"Failed to create model '{model_name}': {str(e)}")
    
    # 提交所有成功的创建
    if created_models:
        db.commit()
    else:
        db.rollback()
    
    return BatchCreateModelsResponse(
        created_count=len(created_models),
        failed_count=len(errors),
        created_models=created_models,
        errors=errors
    )