import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import engine, Base, SessionLocal
from app.services.auth_service import seed_default_users
from app.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 自动创建数据库表 (如果不存在)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 自动初始化种子数据 (admin/editor 账号)
    async with SessionLocal() as db:
        await seed_default_users(db)
        
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Root route
@app.get("/")
async def root():
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "docs_url": "/docs"
    }

# Health check route
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Mount uploads static folder
if not os.path.exists("uploads"):
    os.makedirs("uploads")
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Include routers
app.include_router(api_router, prefix=settings.API_V1_STR)
