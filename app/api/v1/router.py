from fastapi import APIRouter
from app.api.v1.endpoints import auth, captcha, menu, user, role, dict, notification, config, material, screen

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(captcha.router, prefix="/captcha", tags=["captcha"])
api_router.include_router(menu.router, prefix="/menu", tags=["menu"])
api_router.include_router(user.router, prefix="/user", tags=["user"])
api_router.include_router(role.router, prefix="/role", tags=["role"])
api_router.include_router(dict.router, prefix="/dict", tags=["dict"])
api_router.include_router(notification.router, prefix="/notification", tags=["notification"])
api_router.include_router(config.router, prefix="/config", tags=["config"])
api_router.include_router(material.router, prefix="/materials", tags=["materials"])
api_router.include_router(screen.router, prefix="/screens", tags=["screens"])


