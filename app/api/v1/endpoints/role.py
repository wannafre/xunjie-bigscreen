from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import check_permissions
from app.schemas.role import RoleCreate, RoleUpdate, RoleOut, RolePaginationOut
from app.crud import role as crud_role

router = APIRouter()

@router.post("/", response_model=RoleOut, status_code=status.HTTP_201_CREATED)
async def create_role_endpoint(
    role_in: RoleCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:role:add"))
):
    """
    Create a new role and bind menus.
    """
    existing_role = await crud_role.get_role_by_key(db, role_in.role_key)
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role key identifier already exists"
        )
    return await crud_role.create_role(db, role_in)

@router.get("/", response_model=RolePaginationOut)
async def list_roles_endpoint(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页大小"),
    role_name: Optional[str] = Query(None, description="按名称过滤角色"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:role:list"))
):
    """
    Get list of all roles.
    """
    skip = (page - 1) * page_size
    total, items = await crud_role.get_all_roles(db, skip=skip, limit=page_size, role_name=role_name)
    return {"total": total, "items": items}

@router.get("/{role_id}", response_model=RoleOut)
async def get_role_endpoint(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:role:query"))
):
    """
    Get role details.
    """
    role = await crud_role.get_role_by_id(db, role_id)
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return role

@router.put("/{role_id}", response_model=RoleOut)
async def update_role_endpoint(
    role_id: int,
    role_in: RoleUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:role:edit"))
):
    """
    Update role and its menu bindings.
    """
    db_role = await crud_role.get_role_by_id(db, role_id)
    if not db_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return await crud_role.update_role(db, db_role, role_in)

@router.delete("/{role_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_role_endpoint(
    role_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:role:remove"))
):
    """
    Delete role.
    """
    success = await crud_role.delete_role(db, role_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Role not found"
        )
    return None
