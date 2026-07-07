from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.schemas.screen import ScreenCreate, ScreenUpdate, ScreenOut
from app.crud import screen as crud_screen

router = APIRouter()

@router.get("/", response_model=List[ScreenOut])
async def list_my_screens(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取当前用户创建的所有大屏项目列表
    """
    return await crud_screen.get_user_screens(db, current_user.id)

@router.get("/{screen_id}", response_model=ScreenOut)
async def get_screen_detail(
    screen_id: int,
    db: AsyncSession = Depends(get_db),
    token: Optional[str] = Query(None, description="可选Token。如果是已发布的公开大屏，免Token访问；如果是草稿大屏，必须验权")
):
    """
    获取大屏详情配置，主要供画布编辑器和预览页面调用。
    如果大屏已发布(is_published='1')，则允许公开免登录访问，以便预览分享。
    """
    db_screen = await crud_screen.get_screen_by_id(db, screen_id)
    if not db_screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="大屏项目不存在或已删除"
        )
        
    # 如果已发布，允许直接匿名查看
    if db_screen.is_published == "1":
        return db_screen
        
    # 如果未发布，必须校验 Token 所有权
    from app.api.v1.endpoints.auth import get_current_user
    from fastapi.security import OAuth2PasswordBearer
    from jose import jwt
    from app.core.config import settings
    from app.crud.user import get_user_by_username
    
    # 尝试从传入的 Query 或 Authorization header 解析用户
    user = None
    if token:
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username = payload.get("sub")
            if username:
                user = await get_user_by_username(db, username)
        except Exception:
            pass
            
    if not user:
        # Fallback to raising unauthorized if no token was verified
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="此大屏未发布，请登录后访问"
        )
        
    if db_screen.user_id != user.id and user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权查看此未发布大屏"
        )
        
    return db_screen

@router.post("/", response_model=ScreenOut, status_code=status.HTTP_201_CREATED)
async def create_new_screen(
    screen_in: ScreenCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    新建一个大屏项目 (默认未发布状态)
    """
    return await crud_screen.create_screen(db, screen_in, current_user.id, current_user.username)

@router.put("/{screen_id}", response_model=ScreenOut)
async def update_screen_detail(
    screen_id: int,
    screen_in: ScreenUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    保存/更新大屏的画布大小、背景、组件布局及图表属性 option 数据
    """
    db_screen = await crud_screen.get_screen_by_id(db, screen_id)
    if not db_screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="大屏项目未找到"
        )
    # 鉴权：只有拥有者或超级管理员可以编辑
    if db_screen.user_id != current_user.id and current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权修改此大屏"
        )
    return await crud_screen.update_screen(db, db_screen, screen_in, current_user.username)

@router.delete("/{screen_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_screen_project(
    screen_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    软删除大屏项目
    """
    db_screen = await crud_screen.get_screen_by_id(db, screen_id)
    if not db_screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="大屏项目未找到"
        )
    if db_screen.user_id != current_user.id and current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="您无权删除此大屏"
        )
    await crud_screen.delete_screen(db, screen_id)
    return None

@router.post("/{screen_id}/publish", response_model=ScreenOut)
async def toggle_screen_publish(
    screen_id: int,
    is_published: str = Query(..., description="发布状态：'0'草稿，'1'发布"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    发布或下线大屏项目
    """
    db_screen = await crud_screen.get_screen_by_id(db, screen_id)
    if not db_screen:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="大屏项目未找到"
        )
    if db_screen.user_id != current_user.id and current_user.username != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此大屏"
        )
        
    screen_update = ScreenUpdate(is_published=is_published)
    return await crud_screen.update_screen(db, db_screen, screen_update, current_user.username)
