from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.models.role import Role
from app.models.menu import Menu
from app.schemas.role import RoleCreate, RoleUpdate

async def get_role_by_id(db: AsyncSession, role_id: int) -> Optional[Role]:
    """
    Get a role by its ID.
    """
    result = await db.execute(select(Role).filter(Role.id == role_id))
    return result.scalars().first()

async def get_role_by_key(db: AsyncSession, role_key: str) -> Optional[Role]:
    """
    Get a role by its unique key.
    """
    result = await db.execute(select(Role).filter(Role.role_key == role_key))
    return result.scalars().first()

async def get_all_roles(db: AsyncSession) -> List[Role]:
    """
    Get all roles.
    """
    result = await db.execute(select(Role))
    return list(result.scalars().all())

async def create_role(db: AsyncSession, role_in: RoleCreate) -> Role:
    """
    Create a new role and associate specified menus.
    """
    role_data = role_in.model_dump(exclude={"menu_ids"})
    db_role = Role(**role_data)
    
    if role_in.menu_ids:
        res = await db.execute(select(Menu).filter(Menu.id.in_(role_in.menu_ids)))
        db_role.menus = res.scalars().all()
        
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def update_role(db: AsyncSession, db_role: Role, role_in: RoleUpdate) -> Role:
    """
    Update a role and its associated menus.
    """
    update_data = role_in.model_dump(exclude_unset=True)
    
    if "menu_ids" in update_data:
        menu_ids = update_data["menu_ids"]
        if menu_ids:
            res = await db.execute(select(Menu).filter(Menu.id.in_(menu_ids)))
            db_role.menus = res.scalars().all()
        else:
            db_role.menus = []
        del update_data["menu_ids"]
        
    for field, value in update_data.items():
        setattr(db_role, field, value)
        
    db.add(db_role)
    await db.commit()
    await db.refresh(db_role)
    return db_role

async def delete_role(db: AsyncSession, role_id: int) -> bool:
    """
    Delete a role.
    """
    db_role = await get_role_by_id(db, role_id)
    if not db_role:
        return False
    await db.delete(db_role)
    await db.commit()
    return True
