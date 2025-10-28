"""系统提示词管理API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.utils.database import get_db
from app.models.system_prompt import (
    SystemPromptDB, SystemPromptCreate, SystemPromptUpdate, SystemPromptResponse
)

router = APIRouter()


@router.get("/", response_model=List[SystemPromptResponse])
async def list_system_prompts(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取系统提示词列表"""
    query = db.query(SystemPromptDB)
    
    if category:
        query = query.filter(SystemPromptDB.category == category)
    
    prompts = query.offset(skip).limit(limit).all()
    return prompts


@router.get("/{prompt_id}", response_model=SystemPromptResponse)
async def get_system_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """获取单个系统提示词"""
    prompt = db.query(SystemPromptDB).filter(SystemPromptDB.id == prompt_id).first()
    if not prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")
    return prompt


@router.post("/", response_model=SystemPromptResponse, status_code=status.HTTP_201_CREATED)
async def create_system_prompt(
    prompt: SystemPromptCreate,
    db: Session = Depends(get_db)
):
    """创建系统提示词"""
    # 检查名称是否已存在
    existing = db.query(SystemPromptDB).filter(SystemPromptDB.name == prompt.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="System prompt name already exists")
    
    db_prompt = SystemPromptDB(**prompt.model_dump())
    db.add(db_prompt)
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


@router.put("/{prompt_id}", response_model=SystemPromptResponse)
async def update_system_prompt(
    prompt_id: int,
    prompt: SystemPromptUpdate,
    db: Session = Depends(get_db)
):
    """更新系统提示词"""
    db_prompt = db.query(SystemPromptDB).filter(SystemPromptDB.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")
    
    # 如果更新名称，检查是否重复
    if prompt.name and prompt.name != db_prompt.name:
        existing = db.query(SystemPromptDB).filter(SystemPromptDB.name == prompt.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="System prompt name already exists")
    
    # 更新字段
    update_data = prompt.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_prompt, field, value)
    
    db.commit()
    db.refresh(db_prompt)
    return db_prompt


@router.delete("/{prompt_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_system_prompt(prompt_id: int, db: Session = Depends(get_db)):
    """删除系统提示词"""
    db_prompt = db.query(SystemPromptDB).filter(SystemPromptDB.id == prompt_id).first()
    if not db_prompt:
        raise HTTPException(status_code=404, detail="System prompt not found")
    
    db.delete(db_prompt)
    db.commit()
    return None


@router.get("/categories/list", response_model=List[str])
async def list_categories(db: Session = Depends(get_db)):
    """获取所有分类"""
    categories = db.query(SystemPromptDB.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]
