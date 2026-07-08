from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from app.models.dict import DictType, DictData
from app.schemas.dict import DictTypeCreate, DictTypeUpdate, DictDataCreate, DictDataUpdate

# Dict Type CRUD
async def get_dict_type_by_id(db: AsyncSession, dict_id: int) -> Optional[DictType]:
    result = await db.execute(select(DictType).filter(DictType.dict_id == dict_id))
    return result.scalars().first()

async def get_dict_type_by_type(db: AsyncSession, dict_type: str) -> Optional[DictType]:
    result = await db.execute(select(DictType).filter(DictType.dict_type == dict_type))
    return result.scalars().first()

async def get_all_dict_types(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 100,
    dict_name: Optional[str] = None
) -> tuple[int, List[DictType]]:
    """
    Get all dictionary types with pagination and optional name filter.
    """
    query = select(DictType)
    if dict_name:
        query = query.filter(DictType.dict_name.like(f"%{dict_name}%"))

    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(DictType.dict_id.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return total, list(result.scalars().all())

async def create_dict_type(db: AsyncSession, type_in: DictTypeCreate) -> DictType:
    db_type = DictType(**type_in.model_dump())
    db.add(db_type)
    await db.commit()
    await db.refresh(db_type)
    return db_type

async def update_dict_type(db: AsyncSession, db_type: DictType, type_in: DictTypeUpdate) -> DictType:
    update_data = type_in.model_dump(exclude_unset=True)
    
    # If dict_type changes, we also need to update all associated dict_data type fields
    old_type = db_type.dict_type
    new_type = update_data.get("dict_type")
    
    for field, value in update_data.items():
        setattr(db_type, field, value)
        
    db.add(db_type)
    
    if new_type and new_type != old_type:
        # Update associated dict_data
        from sqlalchemy import update
        await db.execute(
            update(DictData)
            .where(DictData.dict_type == old_type)
            .values(dict_type=new_type)
        )
        
    await db.commit()
    await db.refresh(db_type)
    return db_type

async def delete_dict_type(db: AsyncSession, dict_id: int) -> bool:
    db_type = await get_dict_type_by_id(db, dict_id)
    if not db_type:
        return False
    
    # Delete associated dict data
    from sqlalchemy import delete
    await db.execute(delete(DictData).where(DictData.dict_type == db_type.dict_type))
    
    await db.delete(db_type)
    await db.commit()
    return True


# Dict Data CRUD
async def get_dict_data_by_id(db: AsyncSession, dict_code: int) -> Optional[DictData]:
    result = await db.execute(select(DictData).filter(DictData.dict_code == dict_code))
    return result.scalars().first()

async def get_dict_data_by_type(
    db: AsyncSession,
    dict_type: str,
    skip: int = 0,
    limit: int = 100,
    dict_label: Optional[str] = None
) -> tuple[int, List[DictData]]:
    """
    Get dictionary data by type with pagination and optional label filter.
    """
    query = select(DictData).filter(DictData.dict_type == dict_type)
    if dict_label:
        query = query.filter(DictData.dict_label.like(f"%{dict_label}%"))

    from sqlalchemy import func
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    query = query.order_by(DictData.dict_sort.asc()).offset(skip).limit(limit)
    result = await db.execute(query)
    return total, list(result.scalars().all())

async def create_dict_data(db: AsyncSession, data_in: DictDataCreate) -> DictData:
    db_data = DictData(**data_in.model_dump())
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data

async def update_dict_data(db: AsyncSession, db_data: DictData, data_in: DictDataUpdate) -> DictData:
    update_data = data_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_data, field, value)
    db.add(db_data)
    await db.commit()
    await db.refresh(db_data)
    return db_data

async def delete_dict_data(db: AsyncSession, dict_code: int) -> bool:
    db_data = await get_dict_data_by_id(db, dict_code)
    if not db_data:
        return False
    await db.delete(db_data)
    await db.commit()
    return True
