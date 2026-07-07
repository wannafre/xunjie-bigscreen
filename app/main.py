import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from app.core.config import settings
from app.api.v1.router import api_router
from app.core.database import engine, Base, SessionLocal
from app.services.auth_service import seed_default_users
from app.models.user import User

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 检查数据库是否已经初始化（通过尝试查询 users 表来判断）
    db_initialized = False
    try:
        async with SessionLocal() as db:
            await db.execute(text("SELECT 1 FROM users LIMIT 1"))
            db_initialized = True
    except Exception:
        pass

    if not db_initialized:
        # 只有在数据库未初始化时，才自动创建数据库表和初始化种子数据
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        
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
