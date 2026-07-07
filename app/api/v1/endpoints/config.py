from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.v1.endpoints.auth import check_permissions
from app.schemas.config import SystemConfigOut, SystemConfigUpdate
from app.crud import config as crud_config

router = APIRouter()

@router.get("/", response_model=List[SystemConfigOut])
async def list_configs(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:config:list"))
):
    """
    Get all configurations (Admin only).
    """
    return await crud_config.get_all_configs(db)

@router.put("/{config_key}", response_model=SystemConfigOut)
async def update_config_endpoint(
    config_key: str,
    config_in: SystemConfigUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:config:edit"))
):
    """
    Update a config key (Admin only).
    """
    config = await crud_config.get_config_by_key(db, config_key)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Configuration key not found"
        )
    return await crud_config.update_config(db, config_key, config_in.config_value)
