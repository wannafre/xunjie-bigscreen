from datetime import datetime, timedelta
from typing import Any, Optional
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.crud.user import get_user_by_username
from app.schemas.user import UserOut
from app.services.auth_service import authenticate_user
from app.core.captcha import captcha_manager, verify_captcha_verification
from app.core.response import make_response, ResponseCode

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Pydantic Schemas
class LoginRequest(BaseModel):
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="密码")
    captchaVerification: Optional[str] = Field(default=None, description="验证码校验凭证")

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

def get_client_ip(request: Request) -> str:
    forwarded = request.headers.get("X-Forwarded-For")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "127.0.0.1"

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception

    # Enforce: users without role or menus associated with role cannot access backend
    if user.username != "admin":
        active_roles = [r for r in user.roles if r.status == "0"]
        if not active_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="没有分配角色或角色已被停用，禁止访问后台！"
            )
        has_menu = False
        for r in active_roles:
            for m in r.menus:
                if m.status == "0":
                    has_menu = True
                    break
            if has_menu:
                break
        if not has_menu:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="角色下未分配任何菜单，禁止访问后台！"
            )

    return user

async def get_current_front_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> Any:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await get_user_by_username(db, username)
    if user is None:
        raise credentials_exception

    return user

def check_permissions(required_perm: str):
    """
    FastAPI dependency to check if the current user has the specified permission.
    """
    async def dependency(current_user: Any = Depends(get_current_user)) -> Any:
        if current_user.username == "admin":
            return current_user
        if required_perm not in current_user.permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足，需要权限: {required_perm}"
            )
        return current_user
    return dependency


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    ip = get_client_ip(request)
    username = login_data.username
    policy = settings.CAPTCHA_POLICY
    
    # 记录该IP的请求，用于频率统计
    captcha_manager.record_ip_request(ip)
    
    captcha_required = False
    
    if policy == 1:
        # 始终开启验证码
        captcha_required = True
    elif policy == 2:
        # 智能触发策略：密码错误次数达标，或者同IP请求过于频繁
        user_fails = captcha_manager.get_fail_count(username)
        ip_fails = captcha_manager.get_fail_count(ip)
        ip_rate = captcha_manager.get_ip_request_rate(ip, settings.CAPTCHA_IP_LIMIT_PERIOD)
        
        if (user_fails >= settings.CAPTCHA_MAX_FAILURES or 
            ip_fails >= settings.CAPTCHA_MAX_FAILURES or 
            ip_rate >= settings.CAPTCHA_IP_LIMIT_COUNT):
            captcha_required = True
            
    # 如果需要验证码，校验验证码凭证
    if captcha_required:
        if not login_data.captchaVerification:
            return make_response(
                status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                code=ResponseCode.CAPTCHA_REQUIRED,
                message="需要验证码验证"
            )
            
        # 验证凭证合法性 (一次性消费，防止重放)
        is_valid = verify_captcha_verification(login_data.captchaVerification)
        if not is_valid:
            return make_response(
                status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                code=ResponseCode.CAPTCHA_REQUIRED,
                message="验证码失效或验证未通过"
            )

    # 进行用户名/密码认证
    user = await authenticate_user(db, username, login_data.password)
    if not user:
        # 登录失败，累加该用户名和该IP的失败计数
        captcha_manager.record_fail(username)
        captcha_manager.record_fail(ip)
        return make_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ResponseCode.INVALID_CREDENTIALS,
            message="用户名或密码错误"
        )
        
    # Enforce: users without role or menus associated with role cannot access backend
    if user.username != "admin":
        active_roles = [r for r in user.roles if r.status == "0"]
        if not active_roles:
            return make_response(
                status_code=status.HTTP_403_FORBIDDEN,
                code=ResponseCode.FORBIDDEN,
                message="没有分配角色或角色已被停用，禁止登录后台！"
            )
        has_menu = False
        for r in active_roles:
            for m in r.menus:
                if m.status == "0":
                    has_menu = True
                    break
            if has_menu:
                break
        if not has_menu:
            return make_response(
                status_code=status.HTTP_403_FORBIDDEN,
                code=ResponseCode.FORBIDDEN,
                message="角色下未分配任何菜单，禁止登录后台！"
            )

    # 认证成功，重置失败次数计数器
    captcha_manager.reset_fail(username)
    captcha_manager.reset_fail(ip)
    
    # 更新最后登录时间和最后登录IP
    user.login_date = datetime.utcnow() + timedelta(hours=8)
    user.login_ip = ip
    db.add(user)
    await db.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/info", response_model=UserOut)
async def get_info(current_user: Any = Depends(get_current_user)) -> Any:
    return current_user

@router.post("/logout")
async def logout() -> Any:
    return {"message": "Success"}

@router.post("/login/front", response_model=Token)
async def login_front(
    request: Request,
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
) -> Any:
    ip = get_client_ip(request)
    username = login_data.username
    policy = settings.CAPTCHA_POLICY
    
    # 记录该IP的请求，用于频率统计
    captcha_manager.record_ip_request(ip)
    
    captcha_required = False
    
    if policy == 1:
        # 始终开启验证码
        captcha_required = True
    elif policy == 2:
        # 智能触发策略：密码错误次数达标，或者同IP请求过于频繁
        user_fails = captcha_manager.get_fail_count(username)
        ip_fails = captcha_manager.get_fail_count(ip)
        ip_rate = captcha_manager.get_ip_request_rate(ip, settings.CAPTCHA_IP_LIMIT_PERIOD)
        
        if (user_fails >= settings.CAPTCHA_MAX_FAILURES or 
            ip_fails >= settings.CAPTCHA_MAX_FAILURES or 
            ip_rate >= settings.CAPTCHA_IP_LIMIT_COUNT):
            captcha_required = True
            
    # 如果需要验证码，校验验证码凭证
    if captcha_required:
        if not login_data.captchaVerification:
            return make_response(
                status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                code=ResponseCode.CAPTCHA_REQUIRED,
                message="需要验证码验证"
            )
            
        # 验证凭证合法性 (一次性消费，防止重放)
        is_valid = verify_captcha_verification(login_data.captchaVerification)
        if not is_valid:
            return make_response(
                status_code=status.HTTP_428_PRECONDITION_REQUIRED,
                code=ResponseCode.CAPTCHA_REQUIRED,
                message="验证码失效或验证未通过"
            )

    # 进行用户名/密码认证
    user = await authenticate_user(db, username, login_data.password)
    if not user:
        # 登录失败，累加该用户名和该IP的失败计数
        captcha_manager.record_fail(username)
        captcha_manager.record_fail(ip)
        return make_response(
            status_code=status.HTTP_400_BAD_REQUEST,
            code=ResponseCode.INVALID_CREDENTIALS,
            message="用户名或密码错误"
        )
        
    # C端登录免除角色、菜单分配检查

    # 认证成功，重置失败次数计数器
    captcha_manager.reset_fail(username)
    captcha_manager.reset_fail(ip)
    
    # 更新最后登录时间和最后登录IP
    user.login_date = datetime.utcnow() + timedelta(hours=8)
    user.login_ip = ip
    db.add(user)
    await db.commit()
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/info/front", response_model=UserOut)
async def get_info_front(current_user: Any = Depends(get_current_front_user)) -> Any:
    return current_user

@router.post("/logout/front")
async def logout_front() -> Any:
    return {"message": "Success"}



