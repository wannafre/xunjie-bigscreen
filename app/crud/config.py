from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from app.models.config import SystemConfig
from app.schemas.config import SystemConfigUpdate

async def get_config_by_key(db: AsyncSession, config_key: str) -> Optional[SystemConfig]:
    """Retrieve config by unique key."""
    result = await db.execute(select(SystemConfig).filter(SystemConfig.config_key == config_key))
    return result.scalars().first()

async def get_all_configs(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[SystemConfig]:
    """Retrieve all configuration variables."""
    result = await db.execute(select(SystemConfig).offset(skip).limit(limit))
    return list(result.scalars().all())

async def update_config(db: AsyncSession, config_key: str, value: str) -> Optional[SystemConfig]:
    """Update a specific configuration value."""
    config = await get_config_by_key(db, config_key)
    if config:
        config.config_value = value
        db.add(config)
        await db.commit()
        await db.refresh(config)
        
        # Reset storage manager provider cache when storage config changes
        if config_key.startswith("sys.storage"):
            from app.services.storage_service import StorageManager
            StorageManager.reset_provider()
            
    return config
