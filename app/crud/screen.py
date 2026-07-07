from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional, List
from app.models.screen import Screen
from app.schemas.screen import ScreenCreate, ScreenUpdate

async def get_screen_by_id(db: AsyncSession, screen_id: int) -> Optional[Screen]:
    """Retrieve screen by ID."""
    result = await db.execute(select(Screen).filter(Screen.id == screen_id, Screen.del_flag == "0"))
    return result.scalars().first()

async def get_user_screens(db: AsyncSession, user_id: int) -> List[Screen]:
    """Get all dashboards created by a user."""
    result = await db.execute(
        select(Screen).filter(Screen.user_id == user_id, Screen.del_flag == "0")
    )
    return list(result.scalars().all())

async def create_screen(db: AsyncSession, screen_in: ScreenCreate, user_id: int, creator_name: str) -> Screen:
    """Create a new big screen dashboard project."""
    obj_data = screen_in.model_dump()
    # Ensure ownership is mapped correctly
    db_screen = Screen(
        **obj_data,
        user_id=user_id,
        create_by=creator_name
    )
    db.add(db_screen)
    await db.commit()
    await db.refresh(db_screen)
    return db_screen

async def update_screen(db: AsyncSession, db_screen: Screen, screen_in: ScreenUpdate, updater_name: str) -> Screen:
    """Update a dashboard layout or configurations."""
    update_data = screen_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_screen, field, value)
    db_screen.update_by = updater_name
    db.add(db_screen)
    await db.commit()
    await db.refresh(db_screen)
    return db_screen

async def delete_screen(db: AsyncSession, screen_id: int) -> bool:
    """Soft delete a dashboard project."""
    db_screen = await get_screen_by_id(db, screen_id)
    if not db_screen:
        return False
    db_screen.del_flag = "2"
    db.add(db_screen)
    await db.commit()
    return True
