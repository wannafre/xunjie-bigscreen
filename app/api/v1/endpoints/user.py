from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import check_permissions, get_current_user
from app.schemas.user import UserCreate, UserUpdate, UserOut, UserProfileUpdate, UserPasswordUpdate
from app.crud import user as crud_user

router = APIRouter()

@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:add"))
):
    """
    Create a new user.
    """
    existing_user = await crud_user.get_user_by_username(db, user_in.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    return await crud_user.create_user(db, user_in)

@router.get("/", response_model=List[UserOut])
async def list_users_endpoint(
    skip: int = 0,
    limit: int = 100,
    username: Optional[str] = None,
    nickname: Optional[str] = None,
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:list"))
):
    """
    Get users list with optional search filters.
    """
    return await crud_user.get_all_users(db, skip=skip, limit=limit, username=username, nickname=nickname, status=status)

@router.get("/{user_id}", response_model=UserOut)
async def get_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:query"))
):
    """
    Get user details.
    """
    db_user = await crud_user.get_user_by_id(db, user_id)
    if not db_user or db_user.del_flag == "2":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return db_user

@router.put("/{user_id}", response_model=UserOut)
async def update_user_endpoint(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:edit"))
):
    """
    Update user.
    """
    db_user = await crud_user.get_user_by_id(db, user_id)
    if not db_user or db_user.del_flag == "2":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return await crud_user.update_user(db, db_user, user_in)

@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:remove"))
):
    """
    Delete user.
    """
    success = await crud_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return None

@router.put("/{user_id}/reset-pwd")
async def reset_user_password_endpoint(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:user:resetPwd"))
):
    """
    Reset user password to a randomly generated string.
    """
    # 1. Cannot reset own password
    if current_user.id == user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不可以重置自己的密码"
        )
    
    # 2. Fetch target user
    db_user = await crud_user.get_user_by_id(db, user_id)
    if not db_user or db_user.del_flag == "2":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
        
    # 3. Cannot reset the super administrator (admin)
    if db_user.username == "admin":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不可以重置超级管理员的密码"
        )
        
    # 4. Generate random password
    import random
    import string
    from app.core.security import get_password_hash
    
    alphabet = string.ascii_letters + string.digits
    new_password = ''.join(random.choices(alphabet, k=12))
    
    # 5. Update user password
    salt = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    hashed_password = get_password_hash(new_password, salt)
    
    db_user.password = hashed_password
    db_user.salt = salt
    db.add(db_user)
    await db.commit()
    
    return {"message": "Success", "new_password": new_password}


@router.put("/profile", response_model=UserOut)
async def update_profile_endpoint(
    profile_in: UserProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update logged-in user's profile info (nickname, email, phonenumber, sex).
    """
    if profile_in.nickname is not None:
        current_user.nickname = profile_in.nickname
    if profile_in.email is not None:
        current_user.email = profile_in.email
    if profile_in.phonenumber is not None:
        current_user.phonenumber = profile_in.phonenumber
    if profile_in.sex is not None:
        current_user.sex = profile_in.sex
        
    db.add(current_user)
    await db.commit()
    await db.refresh(current_user)
    return current_user


@router.put("/profile/update-pwd")
async def update_password_endpoint(
    pwd_in: UserPasswordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update logged-in user's password.
    """
    from app.core.security import verify_password, get_password_hash
    import random
    import string
    
    # 1. Verify old password
    if not verify_password(pwd_in.old_password, current_user.password, current_user.salt):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="原密码错误"
        )
        
    # 2. Update to new password
    new_salt = "".join(random.choices(string.ascii_letters + string.digits, k=16))
    hashed_password = get_password_hash(pwd_in.new_password, new_salt)
    
    current_user.password = hashed_password
    current_user.salt = new_salt
    
    db.add(current_user)
    await db.commit()
    return {"message": "密码修改成功"}

