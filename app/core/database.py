from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import JSON
from typing import AsyncGenerator
from app.core.config import settings

# 1. Custom compiler for MySQL < 5.7.8 to support JSON columns via LONGTEXT
@compiles(JSON, "mysql")
def compile_json_mysql(type_, compiler, **kw):
    try:
        version = compiler.dialect.server_version_info
        if version and version < (5, 7, 8):
            return "LONGTEXT"
    except Exception:
        pass
    return "JSON"

connect_args = {}
if settings.DATABASE_URL.startswith("sqlite"):
    connect_args = {"check_same_thread": False}

# 2. Lazy wrappers to prevent thread/event loop mismatches under Uvicorn reload=True on Windows
class LazyAsyncEngine:
    def __init__(self):
        self._engine = None

    def _get_engine(self):
        if self._engine is None:
            self._engine = create_async_engine(
                settings.DATABASE_URL,
                connect_args=connect_args,
                echo=True,  # Log SQL queries, set to False in production
            )
        return self._engine

    def __getattr__(self, name):
        return getattr(self._get_engine(), name)

class LazySessionmaker:
    def __init__(self):
        self._sessionmaker = None

    def _get_sessionmaker(self):
        global engine
        if self._sessionmaker is None:
            self._sessionmaker = async_sessionmaker(
                bind=engine,
                autocommit=False,
                autoflush=False,
                expire_on_commit=False,
            )
        return self._sessionmaker

    def __call__(self, **local_kw):
        return self._get_sessionmaker()(**local_kw)

    def __getattr__(self, name):
        return getattr(self._get_sessionmaker(), name)

engine = LazyAsyncEngine()
SessionLocal = LazySessionmaker()

class Base(DeclarativeBase):
    pass

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()

