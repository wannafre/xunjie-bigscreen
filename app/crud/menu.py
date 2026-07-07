from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.models.menu import Menu
from app.schemas.menu import MenuCreate, MenuUpdate

async def get_menu_by_id(db: AsyncSession, menu_id: int) -> Optional[Menu]:
    """
    Retrieve menu by primary key ID.
    """
    result = await db.execute(select(Menu).filter(Menu.id == menu_id))
    return result.scalars().first()

async def get_all_menus(db: AsyncSession) -> List[Menu]:
    """
    Retrieve all menus, ordered by order_num.
    """
    result = await db.execute(select(Menu).order_by(Menu.order_num.asc()))
    return result.scalars().all()

async def create_menu(db: AsyncSession, menu_in: MenuCreate) -> Menu:
    """
    Create a new menu.
    """
    menu_data = menu_in.model_dump()
    db_menu = Menu(**menu_data)
    db.add(db_menu)
    await db.commit()
    await db.refresh(db_menu)
    return db_menu

async def update_menu(db: AsyncSession, db_menu: Menu, menu_in: MenuUpdate) -> Menu:
    """
    Update a menu's attributes.
    """
    update_data = menu_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_menu, field, value)
    db.add(db_menu)
    await db.commit()
    await db.refresh(db_menu)
    return db_menu

async def delete_menu(db: AsyncSession, menu_id: int) -> bool:
    """
    Delete a menu. Returns True if deleted, False if not found or cannot delete.
    """
    db_menu = await get_menu_by_id(db, menu_id)
    if not db_menu:
        return False
    
    # Check if this menu has children (sub-menus)
    child_result = await db.execute(select(Menu).filter(Menu.parent_id == menu_id))
    if child_result.scalars().first():
        raise ValueError("该菜单下有子菜单，请先删除子菜单")

    await db.delete(db_menu)
    await db.commit()
    return True
