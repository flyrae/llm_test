"""工具定义管理API"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.utils.database import get_db
from app.models.tool_definition import (
    ToolDefinitionDB, ToolDefinitionCreate, ToolDefinitionUpdate, ToolDefinitionResponse
)

router = APIRouter()


@router.get("/", response_model=List[ToolDefinitionResponse])
async def list_tools(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """获取工具列表"""
    query = db.query(ToolDefinitionDB)
    
    if category:
        query = query.filter(ToolDefinitionDB.category == category)
    
    tools = query.offset(skip).limit(limit).all()
    return tools


@router.get("/{tool_id}", response_model=ToolDefinitionResponse)
async def get_tool(tool_id: int, db: Session = Depends(get_db)):
    """获取单个工具定义"""
    tool = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.id == tool_id).first()
    if not tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    return tool


@router.post("/", response_model=ToolDefinitionResponse, status_code=status.HTTP_201_CREATED)
async def create_tool(
    tool: ToolDefinitionCreate,
    db: Session = Depends(get_db)
):
    """创建工具定义"""
    # 检查名称是否已存在
    existing = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.name == tool.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Tool name already exists")
    
    # 创建数据库记录
    db_tool = ToolDefinitionDB(
        name=tool.name,
        description=tool.description,
        parameters=tool.parameters.model_dump() if tool.parameters else {},
        category=tool.category,
        example_call=tool.example_call,
        tags=tool.tags
    )
    
    db.add(db_tool)
    db.commit()
    db.refresh(db_tool)
    return db_tool


@router.put("/{tool_id}", response_model=ToolDefinitionResponse)
async def update_tool(
    tool_id: int,
    tool: ToolDefinitionUpdate,
    db: Session = Depends(get_db)
):
    """更新工具定义"""
    db_tool = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    # 更新字段
    update_data = tool.model_dump(exclude_unset=True)
    
    # 如果更新名称，检查是否重复
    if "name" in update_data and update_data["name"] != db_tool.name:
        existing = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.name == update_data["name"]).first()
        if existing:
            raise HTTPException(status_code=400, detail="Tool name already exists")
    
    # 处理parameters
    if "parameters" in update_data and update_data["parameters"]:
        update_data["parameters"] = update_data["parameters"].model_dump()
    
    for key, value in update_data.items():
        setattr(db_tool, key, value)
    
    db.commit()
    db.refresh(db_tool)
    return db_tool


@router.delete("/{tool_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tool(tool_id: int, db: Session = Depends(get_db)):
    """删除工具定义"""
    db_tool = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.id == tool_id).first()
    if not db_tool:
        raise HTTPException(status_code=404, detail="Tool not found")
    
    db.delete(db_tool)
    db.commit()
    return None


@router.get("/categories/list")
async def get_categories(db: Session = Depends(get_db)):
    """获取所有工具分类"""
    categories = db.query(ToolDefinitionDB.category).distinct().all()
    return [cat[0] for cat in categories if cat[0]]


@router.post("/batch-import")
async def batch_import_tools(
    tools: List[ToolDefinitionCreate],
    db: Session = Depends(get_db)
):
    """批量导入工具定义"""
    result = {
        "created": 0,
        "skipped": 0,
        "errors": 0,
        "created_tools": [],
        "skipped_tools": [],
        "error_details": []
    }
    
    for tool_data in tools:
        try:
            # 检查名称是否已存在
            existing = db.query(ToolDefinitionDB).filter(
                ToolDefinitionDB.name == tool_data.name
            ).first()
            
            if existing:
                result["skipped"] += 1
                result["skipped_tools"].append({
                    "name": tool_data.name,
                    "reason": "工具名称已存在"
                })
                continue
            
            # 创建数据库记录
            db_tool = ToolDefinitionDB(
                name=tool_data.name,
                description=tool_data.description,
                parameters=tool_data.parameters.model_dump() if tool_data.parameters else {},
                category=tool_data.category,
                example_call=tool_data.example_call,
                tags=tool_data.tags
            )
            
            db.add(db_tool)
            db.flush()  # 获取ID但不提交
            
            result["created"] += 1
            result["created_tools"].append({
                "id": db_tool.id,
                "name": db_tool.name
            })
            
        except Exception as e:
            result["errors"] += 1
            result["error_details"].append({
                "name": tool_data.name if hasattr(tool_data, 'name') else "未知",
                "error": str(e)
            })
    
    # 如果有成功创建的，提交事务
    if result["created"] > 0:
        db.commit()
    
    return result


@router.post("/batch", status_code=status.HTTP_201_CREATED)
async def batch_import_tools(
    tools: List[ToolDefinitionCreate],
    db: Session = Depends(get_db)
):
    """批量导入工具定义"""
    created_tools = []
    skipped_tools = []
    errors = []
    
    for tool in tools:
        try:
            # 检查名称是否已存在
            existing = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.name == tool.name).first()
            if existing:
                skipped_tools.append({
                    "name": tool.name,
                    "reason": "Tool name already exists"
                })
                continue
            
            # 创建数据库记录
            db_tool = ToolDefinitionDB(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters.model_dump() if tool.parameters else {},
                category=tool.category,
                example_call=tool.example_call,
                tags=tool.tags
            )
            
            db.add(db_tool)
            db.flush()  # 获取ID但不提交
            created_tools.append({
                "id": db_tool.id,
                "name": db_tool.name
            })
        except Exception as e:
            errors.append({
                "name": tool.name,
                "error": str(e)
            })
    
    # 提交所有成功的创建
    if created_tools:
        db.commit()
    
    return {
        "created": len(created_tools),
        "skipped": len(skipped_tools),
        "errors": len(errors),
        "created_tools": created_tools,
        "skipped_tools": skipped_tools,
        "error_details": errors
    }


@router.post("/batch", response_model=dict, status_code=status.HTTP_201_CREATED)
async def batch_import_tools(
    tools: List[ToolDefinitionCreate],
    db: Session = Depends(get_db)
):
    """批量导入工具定义
    
    支持一次性导入多个工具定义。返回成功和失败的统计信息。
    """
    success_count = 0
    failed_count = 0
    errors = []
    created_tools = []
    
    for idx, tool in enumerate(tools):
        try:
            # 检查名称是否已存在
            existing = db.query(ToolDefinitionDB).filter(ToolDefinitionDB.name == tool.name).first()
            if existing:
                failed_count += 1
                errors.append({
                    "index": idx,
                    "name": tool.name,
                    "error": f"工具名称 '{tool.name}' 已存在"
                })
                continue
            
            # 创建数据库记录
            db_tool = ToolDefinitionDB(
                name=tool.name,
                description=tool.description,
                parameters=tool.parameters.model_dump() if tool.parameters else {},
                category=tool.category,
                example_call=tool.example_call,
                tags=tool.tags
            )
            
            db.add(db_tool)
            db.flush()  # 获取ID但不提交
            created_tools.append({
                "id": db_tool.id,
                "name": db_tool.name
            })
            success_count += 1
            
        except Exception as e:
            failed_count += 1
            errors.append({
                "index": idx,
                "name": tool.name if hasattr(tool, 'name') else f"工具{idx}",
                "error": str(e)
            })
    
    # 提交所有成功的记录
    db.commit()
    
    return {
        "success_count": success_count,
        "failed_count": failed_count,
        "total": len(tools),
        "created_tools": created_tools,
        "errors": errors
    }
