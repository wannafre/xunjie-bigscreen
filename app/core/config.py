import os
from typing import List, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from datetime import datetime

# Determine configuration files to load.
# Order: .env (local default) -> config.env (default override) -> CONFIG_PATH (explicit override)
_env_files = [".env"]

if os.path.exists("config.env"):
    _env_files.append("config.env")

_custom_config = os.getenv("CONFIG_PATH")
if _custom_config and os.path.exists(_custom_config):
    _env_files.append(_custom_config)

class Settings(BaseSettings):
    PROJECT_NAME: str = "迅捷后台管理系统"
    API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = "supersecretkeyreplaceinproduction"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    DATABASE_URL: str = "sqlite+aiosqlite:///./sqlite.db"
    
    # Storage settings (Local or OSS/S3 bucket)
    STORAGE_TYPE: str = "local" # local or oss
    STORAGE_OSS_ENDPOINT: str = "http://127.0.0.1:9000"
    STORAGE_OSS_BUCKET: str = "bigscreen"
    STORAGE_OSS_ACCESS_KEY: str = ""
    STORAGE_OSS_SECRET_KEY: str = ""
    STORAGE_OSS_REGION: str = "us-east-1"
    STORAGE_OSS_DOMAIN: str = "" # CDN or custom domain URL prefix
    
    # Timezone settings
    TIMEZONE: str = "Asia/Shanghai"
    
    def get_current_time(self) -> datetime:
        from datetime import datetime
        try:
            from zoneinfo import ZoneInfo
            tz = ZoneInfo(self.TIMEZONE)
        except Exception:
            from datetime import timezone, timedelta
            tz = timezone(timedelta(hours=8))
        return datetime.now(tz).replace(tzinfo=None)
    
    # JWT Algorithm
    ALGORITHM: str = "HS256"
    
    # Captcha configurations
    CAPTCHA_POLICY: int = 0  # 0: Never, 1: Always, 2: Intelligent (progressive)
    CAPTCHA_MAX_FAILURES: int = 1  # Password fail limit before captcha triggers (policy 2)
    CAPTCHA_IP_LIMIT_PERIOD: int = 10  # Seconds window for request limit (policy 2)
    CAPTCHA_IP_LIMIT_COUNT: int = 5  # Request count limit within period (policy 2)
    
    # CORS Origins
    BACKEND_CORS_ORIGINS: Union[str, List[str]] = [
        "http://localhost",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
    ]

    @field_validator("BACKEND_CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            if v.startswith("[") and v.endswith("]"):
                import json
                try:
                    return json.loads(v)
                except Exception:
                    pass
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return []

    model_config = SettingsConfigDict(
        env_file=tuple(_env_files),
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

settings = Settings()

