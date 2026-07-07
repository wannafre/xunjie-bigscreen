from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from app.models.material import Material
from app.schemas.material import MaterialCreate, MaterialUpdate

async def get_material_by_id(db: AsyncSession, material_id: int) -> Optional[Material]:
    """Retrieve material by ID."""
    result = await db.execute(select(Material).filter(Material.id == material_id, Material.del_flag == "0"))
    return result.scalars().first()

async def get_official_materials(db: AsyncSession, category: Optional[str] = None) -> List[Material]:
    """Get all official/system materials, optionally filtered by category."""
    query = select(Material).filter(Material.is_official == True, Material.del_flag == "0")
    if category:
        query = query.filter(Material.category == category)
    result = await db.execute(query)
    return list(result.scalars().all())

async def get_user_materials(db: AsyncSession, user_id: int, category: Optional[str] = None) -> List[Material]:
    """Get all private DIY materials owned by a specific user."""
    query = select(Material).filter(
        Material.creator_id == user_id,
        Material.is_official == False,
        Material.del_flag == "0"
    )
    if category:
        query = query.filter(Material.category == category)
    result = await db.execute(query)
    return list(result.scalars().all())

async def create_material(db: AsyncSession, material_in: MaterialCreate, creator_name: str) -> Material:
    """Create a new material template."""
    obj_data = material_in.model_dump()
    db_material = Material(**obj_data, create_by=creator_name)
    db.add(db_material)
    await db.commit()
    await db.refresh(db_material)
    return db_material

async def update_material(db: AsyncSession, db_material: Material, material_in: MaterialUpdate, updater_name: str) -> Material:
    """Update material details."""
    update_data = material_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_material, field, value)
    db_material.update_by = updater_name
    db.add(db_material)
    await db.commit()
    await db.refresh(db_material)
    return db_material

async def delete_material(db: AsyncSession, material_id: int) -> bool:
    """Soft delete a material."""
    db_material = await get_material_by_id(db, material_id)
    if not db_material:
        return False
    db_material.del_flag = "2"
    db.add(db_material)
    await db.commit()
    return True

async def clone_official_material(db: AsyncSession, official_id: int, user_id: int, username: str) -> Optional[Material]:
    """
    Clones/copies an official material into a user's private DIY space.
    """
    official = await get_material_by_id(db, official_id)
    if not official or not official.is_official:
        return None
        
    # Copy all essential fields
    user_material = Material(
        name=f"{official.name} (DIY)",
        category=official.category,
        subcategory=official.subcategory,
        thumbnail=official.thumbnail,
        config_data=official.config_data,  # JSON is copied
        is_official=False,
        creator_id=user_id,
        parent_id=official.id,
        create_by=username
    )
    
    db.add(user_material)
    await db.commit()
    await db.refresh(user_material)
    return user_material
