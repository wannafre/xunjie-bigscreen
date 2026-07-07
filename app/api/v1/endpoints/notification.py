from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update, func, delete
from typing import List, Optional
from datetime import datetime, timedelta

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.endpoints.auth import get_current_user, check_permissions
from app.models.notification import Notification, UserNotification
from app.models.user import User
from app.schemas.notification import NotificationCreate, NotificationOut, NotificationUpdate, NotificationReadUser

router = APIRouter()

# ==========================================
# User Endpoints (No permission check, only authenticated)
# ==========================================

@router.get("/my", response_model=List[NotificationOut])
async def list_my_notifications(
    status: Optional[str] = None,  # '0' unread, '1' read
    type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    List current user's personal notifications (mapped through user_notifications).
    """
    current_time = settings.get_current_time()
    query = (
        select(UserNotification, Notification)
        .join(Notification, UserNotification.notification_id == Notification.id)
        .filter(
            UserNotification.user_id == current_user.id,
            UserNotification.is_deleted == 0,
            Notification.create_time <= current_time,
            (Notification.expire_time.is_(None)) | (Notification.expire_time > current_time)
        )
    )
    if status is not None:
        is_read_val = 1 if status == '1' else 0
        query = query.filter(UserNotification.is_read == is_read_val)
    if type:
        query = query.filter(Notification.type == type)
        
    query = query.order_by(Notification.create_time.desc())
    result = await db.execute(query)
    
    notices = []
    for user_notif, notif in result.all():
        notices.append(NotificationOut(
            id=notif.id,
            title=notif.title,
            content=notif.content,
            type=notif.type,
            create_time=notif.create_time,
            expire_time=notif.expire_time,
            sys_create_time=notif.sys_create_time,
            create_by=notif.create_by,
            user_id=user_notif.user_id,
            is_read=user_notif.is_read,
            read_time=user_notif.read_time,
            is_deleted=user_notif.is_deleted
        ))
    return notices

@router.get("/unread-count")
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get unread count for current user.
    """
    current_time = settings.get_current_time()
    query = (
        select(func.count(UserNotification.id))
        .join(Notification, UserNotification.notification_id == Notification.id)
        .filter(
            UserNotification.user_id == current_user.id,
            UserNotification.is_read == 0,
            UserNotification.is_deleted == 0,
            Notification.create_time <= current_time,
            (Notification.expire_time.is_(None)) | (Notification.expire_time > current_time)
        )
    )
    result = await db.execute(query)
    count = result.scalar() or 0
    return {"count": count}

@router.put("/read-all")
async def mark_all_as_read(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark all unread notifications of the current user as read.
    """
    stmt = (
        update(UserNotification)
        .where(UserNotification.user_id == current_user.id, UserNotification.is_read == 0)
        .values(is_read=1, read_time=settings.get_current_time())
    )
    await db.execute(stmt)
    await db.commit()
    return {"message": "Success"}

@router.put("/{id}/read", response_model=NotificationOut)
async def mark_as_read(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Mark a notification as read (using notification_id).
    """
    result = await db.execute(
        select(UserNotification, Notification)
        .join(Notification, UserNotification.notification_id == Notification.id)
        .filter(UserNotification.notification_id == id, UserNotification.user_id == current_user.id)
    )
    row = result.first()
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    user_notif, notif = row
    if user_notif.is_read == 0:
        user_notif.is_read = 1
        user_notif.read_time = settings.get_current_time()
        db.add(user_notif)
        await db.commit()
        await db.refresh(user_notif)
        
    return NotificationOut(
        id=notif.id,
        title=notif.title,
        content=notif.content,
        type=notif.type,
        create_time=notif.create_time,
        expire_time=notif.expire_time,
        sys_create_time=notif.sys_create_time,
        create_by=notif.create_by,
        user_id=user_notif.user_id,
        is_read=user_notif.is_read,
        read_time=user_notif.read_time,
        is_deleted=user_notif.is_deleted
    )


# ==========================================
# Admin CRUD Management Endpoints (Requires permission checks)
# ==========================================

@router.get("/", response_model=List[NotificationOut])
async def list_notifications_admin(
    status: Optional[str] = None,
    type: Optional[str] = None,
    user_id: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:notification:list"))
):
    """
    List all system notifications with user read status mapping.
    """
    query = select(Notification)
    if type:
        query = query.filter(Notification.type == type)
        
    query = query.order_by(Notification.create_time.desc())
    result = await db.execute(query)
    notifications = result.scalars().all()
    
    notices = []
    for notif in notifications:
        map_query = select(UserNotification).filter(UserNotification.notification_id == notif.id)
        map_result = await db.execute(map_query)
        mappings = map_result.scalars().all()
        
        if not mappings:
            continue
            
        global_map = next((m for m in mappings if m.user_id == -1), None)
        if global_map:
            if user_id is not None and user_id != -1:
                user_map = next((m for m in mappings if m.user_id == user_id), None)
                if not user_map:
                    continue
            notices.append(NotificationOut(
                id=notif.id,
                title=notif.title,
                content=notif.content,
                type=notif.type,
                create_time=notif.create_time,
                expire_time=notif.expire_time,
                sys_create_time=notif.sys_create_time,
                create_by=notif.create_by,
                user_id=-1,
                is_read=0,
                read_time=None,
                is_deleted=0
            ))
        else:
            user_map = mappings[0]
            if user_id is not None and user_map.user_id != user_id:
                continue
            if status is not None:
                is_read_val = 1 if status == '1' else 0
                if user_map.is_read != is_read_val:
                    continue
            notices.append(NotificationOut(
                id=notif.id,
                title=notif.title,
                content=notif.content,
                type=notif.type,
                create_time=notif.create_time,
                expire_time=notif.expire_time,
                sys_create_time=notif.sys_create_time,
                create_by=notif.create_by,
                user_id=user_map.user_id,
                is_read=user_map.is_read,
                read_time=user_map.read_time,
                is_deleted=user_map.is_deleted
            ))
    return notices

@router.post("/", response_model=NotificationOut, status_code=status.HTTP_201_CREATED)
async def create_notification_admin(
    notification_in: NotificationCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:notification:add"))
):
    """
    Create a new notification content body, and link it to user_notifications for recipient user.
    """
    # 1. Create content
    db_notice = Notification(
        title=notification_in.title,
        content=notification_in.content,
        type=notification_in.type,
        create_time=notification_in.create_time or settings.get_current_time(),
        expire_time=notification_in.expire_time,
        sys_create_time=settings.get_current_time(),
        create_by=current_user.username
    )
    db.add(db_notice)
    await db.commit()
    await db.refresh(db_notice)
    
    # 2. Create UserNotification mapping
    if notification_in.user_id == -1:
        # Fetch all active users
        user_result = await db.execute(select(User).filter(User.del_flag == "0"))
        users = user_result.scalars().all()
        for u in users:
            db_user_notif = UserNotification(
                user_id=u.id,
                notification_id=db_notice.id,
                is_read=0
            )
            db.add(db_user_notif)
            
        global_notif = UserNotification(
            user_id=-1,
            notification_id=db_notice.id,
            is_read=0
        )
        db.add(global_notif)
        await db.commit()
        
        return NotificationOut(
            id=db_notice.id,
            title=db_notice.title,
            content=db_notice.content,
            type=db_notice.type,
            create_time=db_notice.create_time,
            expire_time=db_notice.expire_time,
            sys_create_time=db_notice.sys_create_time,
            create_by=db_notice.create_by,
            user_id=-1,
            is_read=0,
            read_time=None,
            is_deleted=0
        )
    else:
        db_user_notif = UserNotification(
            user_id=notification_in.user_id,
            notification_id=db_notice.id,
            is_read=0
        )
        db.add(db_user_notif)
        await db.commit()
        await db.refresh(db_user_notif)
        
        return NotificationOut(
            id=db_notice.id,
            title=db_notice.title,
            content=db_notice.content,
            type=db_notice.type,
            create_time=db_notice.create_time,
            expire_time=db_notice.expire_time,
            sys_create_time=db_notice.sys_create_time,
            create_by=db_notice.create_by,
            user_id=db_user_notif.user_id,
            is_read=db_user_notif.is_read,
            read_time=db_user_notif.read_time,
            is_deleted=db_user_notif.is_deleted
        )

@router.put("/{id}", response_model=NotificationOut)
async def update_notification_admin(
    id: int,
    notification_in: NotificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:notification:edit"))
):
    """
    Update a notification content body.
    """
    result = await db.execute(select(Notification).filter(Notification.id == id))
    db_notice = result.scalars().first()
    if not db_notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    update_data = notification_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_notice, field, value)
        
    db.add(db_notice)
    await db.commit()
    await db.refresh(db_notice)
    
    # Return representation mapping
    res_mapping = await db.execute(
        select(UserNotification).filter(UserNotification.notification_id == db_notice.id)
    )
    mappings = res_mapping.scalars().all()
    global_map = next((m for m in mappings if m.user_id == -1), None)
    user_notif = global_map if global_map else (mappings[0] if mappings else None)
    
    return NotificationOut(
        id=db_notice.id,
        title=db_notice.title,
        content=db_notice.content,
        type=db_notice.type,
        create_time=db_notice.create_time,
        expire_time=db_notice.expire_time,
        sys_create_time=db_notice.sys_create_time,
        create_by=db_notice.create_by,
        user_id=user_notif.user_id if user_notif else None,
        is_read=user_notif.is_read if user_notif else 0,
        read_time=user_notif.read_time if user_notif else None,
        is_deleted=user_notif.is_deleted if user_notif else 0
    )

@router.get("/{id}/read-users", response_model=List[NotificationReadUser])
async def get_notification_read_users(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:notification:list"))
):
    """
    Get the list of users who have read a specific notification.
    """
    query = (
        select(UserNotification.user_id, User.username, User.nickname, UserNotification.read_time)
        .join(User, UserNotification.user_id == User.id)
        .filter(
            UserNotification.notification_id == id,
            UserNotification.is_read == 1,
            UserNotification.user_id != -1
        )
        .order_by(UserNotification.read_time.desc())
    )
    result = await db.execute(query)
    
    read_users = []
    for user_id, username, nickname, read_time in result.all():
        read_users.append(NotificationReadUser(
            user_id=user_id,
            username=username,
            nickname=nickname,
            read_time=read_time
        ))
    return read_users

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification_admin(
    id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:notification:remove"))
):
    """
    Delete a notification (Admin). Cascades deletion to UserNotification table.
    """
    result = await db.execute(select(Notification).filter(Notification.id == id))
    db_notice = result.scalars().first()
    if not db_notice:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Notification not found"
        )
    
    await db.delete(db_notice)
    await db.commit()
    return None
