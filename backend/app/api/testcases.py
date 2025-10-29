"""测试用例管理API"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
import json
import csv
import io

from app.utils.database import get_db
from app.models.test_case import (
    TestCaseDB, TestCaseCreate, TestCaseUpdate, TestCaseResponse, TestCaseImport
)

router = APIRouter()


@router.get("/", response_model=List[TestCaseResponse])
async def list_test_cases(
    skip: int = 0,
    limit: int = 100,
    category: str = None,
    tags: str = None,
    db: Session = Depends(get_db)
):
    """获取测试用例列表"""
    query = db.query(TestCaseDB)
    
    if category:
        query = query.filter(TestCaseDB.category == category)
    
    if tags:
        query = query.filter(TestCaseDB.tags.contains(tags))
    
    test_cases = query.offset(skip).limit(limit).all()
    return test_cases


@router.get("/{test_case_id}", response_model=TestCaseResponse)
async def get_test_case(test_case_id: int, db: Session = Depends(get_db)):
    """获取单个测试用例"""
    test_case = db.query(TestCaseDB).filter(TestCaseDB.id == test_case_id).first()
    if not test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    return test_case


@router.post("/", response_model=TestCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case: TestCaseCreate,
    db: Session = Depends(get_db)
):
    """创建测试用例"""
    db_test_case = TestCaseDB(
        title=test_case.title,
        category=test_case.category,
        prompt=test_case.prompt,
        system_prompt=test_case.system_prompt,
        conversation_history=test_case.conversation_history,
        expected_output=test_case.expected_output,
        evaluation_criteria=test_case.evaluation_criteria,
        tools=test_case.tools,
        expected_tool_calls=test_case.expected_tool_calls,
        evaluation_weights=test_case.evaluation_weights,
        use_mock=test_case.use_mock,
        tags=test_case.tags,
        meta_data=test_case.meta_data
    )
    
    db.add(db_test_case)
    db.commit()
    db.refresh(db_test_case)
    return db_test_case


@router.put("/{test_case_id}", response_model=TestCaseResponse)
async def update_test_case(
    test_case_id: int,
    test_case: TestCaseUpdate,
    db: Session = Depends(get_db)
):
    """更新测试用例"""
    db_test_case = db.query(TestCaseDB).filter(TestCaseDB.id == test_case_id).first()
    if not db_test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    update_data = test_case.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_test_case, key, value)
    
    db.commit()
    db.refresh(db_test_case)
    return db_test_case


@router.delete("/{test_case_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_test_case(test_case_id: int, db: Session = Depends(get_db)):
    """删除测试用例"""
    db_test_case = db.query(TestCaseDB).filter(TestCaseDB.id == test_case_id).first()
    if not db_test_case:
        raise HTTPException(status_code=404, detail="Test case not found")
    
    db.delete(db_test_case)
    db.commit()
    return None


@router.post("/import", response_model=dict)
async def import_test_cases(
    test_cases: TestCaseImport,
    db: Session = Depends(get_db)
):
    """批量导入测试用例（JSON格式）"""
    created_count = 0
    
    for test_case in test_cases.test_cases:
        db_test_case = TestCaseDB(**test_case.model_dump())
        db.add(db_test_case)
        created_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully imported {created_count} test cases",
        "count": created_count
    }


@router.post("/import/csv", response_model=dict)
async def import_test_cases_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """批量导入测试用例（CSV格式）"""
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="File must be a CSV")
    
    content = await file.read()
    csv_file = io.StringIO(content.decode('utf-8'))
    reader = csv.DictReader(csv_file)
    
    created_count = 0
    for row in reader:
        db_test_case = TestCaseDB(
            title=row.get('title', ''),
            category=row.get('category'),
            prompt=row.get('prompt', ''),
            system_prompt=row.get('system_prompt'),
            expected_output=row.get('expected_output'),
            tags=row.get('tags')
        )
        db.add(db_test_case)
        created_count += 1
    
    db.commit()
    
    return {
        "message": f"Successfully imported {created_count} test cases from CSV",
        "count": created_count
    }
