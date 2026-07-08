from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import check_permissions, get_current_user
from app.schemas.dict import (
    DictTypeCreate, DictTypeUpdate, DictTypeOut, DictTypePaginationOut,
    DictDataCreate, DictDataUpdate, DictDataOut, DictDataPaginationOut
)
from app.crud import dict as crud_dict

router = APIRouter()

# Dict Type Endpoints
@router.post("/type", response_model=DictTypeOut, status_code=status.HTTP_201_CREATED)
async def create_dict_type_endpoint(
    type_in: DictTypeCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:add"))
):
    """
    Create a new dictionary type.
    """
    existing_type = await crud_dict.get_dict_type_by_type(db, type_in.dict_type)
    if existing_type:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dictionary type identifier already exists"
        )
    return await crud_dict.create_dict_type(db, type_in)

@router.get("/type", response_model=DictTypePaginationOut)
async def list_dict_types_endpoint(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    dict_name: Optional[str] = Query(None, description="按名称模糊搜索"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:list"))
):
    """
    Get all dictionary types with pagination.
    """
    skip = (page - 1) * page_size
    total, items = await crud_dict.get_all_dict_types(db, skip=skip, limit=page_size, dict_name=dict_name)
    return {"total": total, "items": items}

@router.get("/type/{dict_id}", response_model=DictTypeOut)
async def get_dict_type_endpoint(
    dict_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:query"))
):
    """
    Get dictionary type details.
    """
    db_type = await crud_dict.get_dict_type_by_id(db, dict_id)
    if not db_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary type not found"
        )
    return db_type

@router.put("/type/{dict_id}", response_model=DictTypeOut)
async def update_dict_type_endpoint(
    dict_id: int,
    type_in: DictTypeUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:edit"))
):
    """
    Update a dictionary type.
    """
    db_type = await crud_dict.get_dict_type_by_id(db, dict_id)
    if not db_type:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary type not found"
        )
    return await crud_dict.update_dict_type(db, db_type, type_in)

@router.delete("/type/{dict_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dict_type_endpoint(
    dict_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:remove"))
):
    """
    Delete a dictionary type.
    """
    success = await crud_dict.delete_dict_type(db, dict_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary type not found"
        )
    return None


# Dict Data Endpoints
@router.post("/data", response_model=DictDataOut, status_code=status.HTTP_201_CREATED)
async def create_dict_data_endpoint(
    data_in: DictDataCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:add"))
):
    """
    Create a new dictionary data.
    """
    return await crud_dict.create_dict_data(db, data_in)

@router.get("/data", response_model=DictDataPaginationOut)
async def list_dict_data_endpoint(
    dict_type: str = Query(..., description="字典类型标识"),
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    dict_label: Optional[str] = Query(None, description="按标签模糊搜索"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:list"))
):
    """
    Get dictionary data list filtered by dictionary type with pagination.
    """
    skip = (page - 1) * page_size
    total, items = await crud_dict.get_dict_data_by_type(db, dict_type, skip=skip, limit=page_size, dict_label=dict_label)
    return {"total": total, "items": items}

@router.get("/data/{dict_code}", response_model=DictDataOut)
async def get_dict_data_endpoint(
    dict_code: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:query"))
):
    """
    Get dictionary data details.
    """
    db_data = await crud_dict.get_dict_data_by_id(db, dict_code)
    if not db_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary data not found"
        )
    return db_data

@router.put("/data/{dict_code}", response_model=DictDataOut)
async def update_dict_data_endpoint(
    dict_code: int,
    data_in: DictDataUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:edit"))
):
    """
    Update dictionary data.
    """
    db_data = await crud_dict.get_dict_data_by_id(db, dict_code)
    if not db_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary data not found"
        )
    return await crud_dict.update_dict_data(db, db_data, data_in)

@router.delete("/data/{dict_code}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dict_data_endpoint(
    dict_code: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:dict:remove"))
):
    """
    Delete dictionary data.
    """
    success = await crud_dict.delete_dict_data(db, dict_code)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dictionary data not found"
        )
    return None

# Public/Helper: Get Dict Data by Type (without specific dict:list permission or token login validation)
@router.get("/data/type/{dict_type}", response_model=List[DictDataOut])
async def get_dict_data_by_type_endpoint(
    dict_type: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get active dictionary data options by type for UI inputs.
    """
    _total, items = await crud_dict.get_dict_data_by_type(db, dict_type, skip=0, limit=1000)
    return items
