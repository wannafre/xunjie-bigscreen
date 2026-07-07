import os
import uuid
import logging
import time
from abc import ABC, abstractmethod
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from fastapi import HTTPException, status
from app.models.config import SystemConfig

logger = logging.getLogger(__name__)

# Try importing boto3 for S3/OSS uploads
try:
    import boto3
    from botocore.exceptions import BotoCoreError, ClientError
except ImportError:
    boto3 = None
    BotoCoreError = Exception
    ClientError = Exception

class StorageProvider(ABC):
    @abstractmethod
    async def save_file(self, file_data: bytes, filename: str, folder: str = "") -> str:
        """
        Saves a file and returns its access URL.
        """
        pass

    @abstractmethod
    async def delete_file(self, file_url: str) -> bool:
        """
        Deletes a file based on its URL/path.
        """
        pass

    @abstractmethod
    async def cleanup_temp_files(self, db_urls: set, max_age_seconds: int = 3600) -> int:
        """
        Deletes any files in storage that are not in the db_urls set and are older than max_age_seconds.
        Returns the number of deleted files.
        """
        pass


class LocalStorageProvider(StorageProvider):
    def __init__(self, base_dir: str = "uploads", base_url: str = "/uploads"):
        self.base_dir = base_dir
        self.base_url = base_url
        if not os.path.exists(self.base_dir):
            os.makedirs(self.base_dir)

    async def save_file(self, file_data: bytes, filename: str, folder: str = "") -> str:
        # Generate safe unique filename
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        
        target_dir = os.path.join(self.base_dir, folder) if folder else self.base_dir
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        file_path = os.path.join(target_dir, unique_name)
        with open(file_path, "wb") as f:
            f.write(file_data)
            
        url_path = f"{self.base_url}/{folder}/{unique_name}" if folder else f"{self.base_url}/{unique_name}"
        # Normalize slashes for URL
        return url_path.replace("\\", "/")

    async def delete_file(self, file_url: str) -> bool:
        try:
            # Extract relative path from URL (e.g., /uploads/filename -> uploads/filename)
            rel_path = file_url.lstrip("/")
            # Verify if it starts with the base URL name
            base_url_stripped = self.base_url.lstrip("/")
            if rel_path.startswith(base_url_stripped):
                path_in_dir = rel_path[len(base_url_stripped):].lstrip("/")
                full_path = os.path.join(self.base_dir, path_in_dir)
                if os.path.exists(full_path):
                    os.remove(full_path)
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to delete local file {file_url}: {e}")
            return False

    async def cleanup_temp_files(self, db_urls: set, max_age_seconds: int = 3600) -> int:
        deleted_count = 0
        now = time.time()
        
        # Traverse base_dir recursively
        for root, dirs, files in os.walk(self.base_dir):
            for file in files:
                full_path = os.path.join(root, file)
                # Calculate relative path relative to base_dir
                rel_path = os.path.relpath(full_path, self.base_dir).replace("\\", "/")
                # Reconstruct the file URL path, e.g. /uploads/folder/filename
                file_url = f"{self.base_url}/{rel_path}"
                
                # Check age of file (mtime)
                try:
                    file_stat = os.stat(full_path)
                    file_age = now - file_stat.st_mtime
                    if file_url not in db_urls and file_age > max_age_seconds:
                        os.remove(full_path)
                        deleted_count += 1
                except Exception as e:
                    logger.error(f"Error checking/deleting file {full_path}: {e}")
                    
        return deleted_count


class OSSStorageProvider(StorageProvider):
    def __init__(self, endpoint: str, bucket: str, access_key: str, secret_key: str, region: str = "", custom_domain: str = ""):
        if not boto3:
            raise RuntimeError("存储桶上传服务需要 boto3 依赖库，请运行 `pip install boto3` 安装后使用。")
        self.endpoint = endpoint
        self.bucket = bucket
        self.access_key = access_key
        self.secret_key = secret_key
        self.region = region or None
        self.custom_domain = custom_domain.rstrip("/")

        # Initialize boto3 S3 Client
        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            region_name=self.region,
            config=boto3.session.Config(signature_version="s3v4")
        )

    async def save_file(self, file_data: bytes, filename: str, folder: str = "") -> str:
        ext = os.path.splitext(filename)[1]
        unique_name = f"{uuid.uuid4().hex}{ext}"
        object_key = f"{folder}/{unique_name}" if folder else unique_name

        try:
            # Upload to S3/OSS
            self.client.put_object(
                Bucket=self.bucket,
                Key=object_key,
                Body=file_data,
                ACL="public-read"  # Make public read
            )
            
            # Generate public URL
            if self.custom_domain:
                return f"{self.custom_domain}/{object_key}"
            
            # Fallback to standard S3 endpoint pattern
            endpoint_clean = self.endpoint.replace("http://", "").replace("https://", "")
            protocol = "https" if self.endpoint.startswith("https") else "http"
            return f"{protocol}://{self.bucket}.{endpoint_clean}/{object_key}"
            
        except (BotoCoreError, ClientError) as e:
            logger.error(f"OSS upload failed: {e}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"对象存储上传失败: {str(e)}"
            )

    async def delete_file(self, file_url: str) -> bool:
        try:
            # Parse object key from URL
            # If using custom domain
            object_key = ""
            if self.custom_domain and file_url.startswith(self.custom_domain):
                object_key = file_url[len(self.custom_domain):].lstrip("/")
            else:
                # Fallback: parse from standard S3 URL structure
                endpoint_clean = self.endpoint.replace("http://", "").replace("https://", "")
                parts = file_url.split(endpoint_clean)
                if len(parts) > 1:
                    object_key = parts[1].lstrip("/")
            
            if object_key:
                self.client.delete_object(Bucket=self.bucket, Key=object_key)
                return True
            return False
        except (BotoCoreError, ClientError) as e:
            logger.error(f"Failed to delete OSS file {file_url}: {e}")
            return False

    async def cleanup_temp_files(self, db_urls: set, max_age_seconds: int = 3600) -> int:
        from datetime import datetime, timezone
        deleted_count = 0
        now = datetime.now(timezone.utc)
        
        try:
            paginator = self.client.get_paginator('list_objects_v2')
            for page in paginator.paginate(Bucket=self.bucket):
                if 'Contents' not in page:
                    continue
                for obj in page['Contents']:
                    object_key = obj['Key']
                    last_modified = obj['LastModified']
                    age_seconds = (now - last_modified).total_seconds()
                    
                    # Construct S3 URL
                    if self.custom_domain:
                        file_url = f"{self.custom_domain}/{object_key}"
                    else:
                        endpoint_clean = self.endpoint.replace("http://", "").replace("https://", "")
                        protocol = "https" if self.endpoint.startswith("https") else "http"
                        file_url = f"{protocol}://{self.bucket}.{endpoint_clean}/{object_key}"
                        
                    if file_url not in db_urls and age_seconds > max_age_seconds:
                        self.client.delete_object(Bucket=self.bucket, Key=object_key)
                        deleted_count += 1
        except Exception as e:
            logger.error(f"Failed to clean up S3 objects: {e}")
            
        return deleted_count


class StorageManager:
    _instance: Optional[StorageProvider] = None
    _current_config_hash: Optional[str] = None

    @classmethod
    async def get_provider(cls, db: AsyncSession) -> StorageProvider:
        """
        Dynamically construct and return the storage provider configured in the DB.
        """
        configs = await cls._fetch_storage_configs(db)
        config_type = configs.get("sys.storage.type", "local")

        # Create a simple hash key to check if configuration changed
        config_signature = f"{config_type}|{configs.get('sys.storage.oss.endpoint')}|{configs.get('sys.storage.oss.bucket')}|{configs.get('sys.storage.oss.access_key')}"

        if cls._instance is None or cls._current_config_hash != config_signature:
            logger.info(f"Loading/Updating Storage Provider configuration: {config_type}")
            if config_type == "oss":
                try:
                    cls._instance = OSSStorageProvider(
                        endpoint=configs.get("sys.storage.oss.endpoint", ""),
                        bucket=configs.get("sys.storage.oss.bucket", ""),
                        access_key=configs.get("sys.storage.oss.access_key", ""),
                        secret_key=configs.get("sys.storage.oss.secret_key", ""),
                        region=configs.get("sys.storage.oss.region", ""),
                        custom_domain=configs.get("sys.storage.oss.domain", "")
                    )
                except Exception as e:
                    logger.error(f"Failed to initialize OSSStorageProvider: {e}. Falling back to local storage.")
                    cls._instance = LocalStorageProvider()
            else:
                cls._instance = LocalStorageProvider()
            cls._current_config_hash = config_signature

        return cls._instance

    @classmethod
    def reset_provider(cls):
        """Reset the cached provider to force reload on the next query."""
        cls._instance = None
        cls._current_config_hash = None

    @classmethod
    async def _fetch_storage_configs(cls, db: AsyncSession) -> dict:
        """
        Helper to fetch all relevant storage key-value configurations from the database.
        """
        keys = [
            "sys.storage.type",
            "sys.storage.oss.endpoint",
            "sys.storage.oss.bucket",
            "sys.storage.oss.access_key",
            "sys.storage.oss.secret_key",
            "sys.storage.oss.region",
            "sys.storage.oss.domain"
        ]
        result = await db.execute(select(SystemConfig).filter(SystemConfig.config_key.in_(keys)))
        db_configs = result.scalars().all()
        
        # Build dictionary with defaults
        config_dict = {
            "sys.storage.type": "local"
        }
        for item in db_configs:
            config_dict[item.config_key] = item.config_value
            
        return config_dict


async def get_all_referenced_urls(db: AsyncSession) -> set:
    """
    Queries database tables and extracts all referenced asset URLs to prevent them from being deleted.
    """
    from app.models.material import Material
    from app.models.screen import Screen
    
    urls = set()
    
    # 1. Scan materials table
    result_m = await db.execute(select(Material))
    materials = result_m.scalars().all()
    for m in materials:
        if m.thumbnail:
            urls.add(m.thumbnail)
        if m.config_data:
            _extract_urls_from_json(m.config_data, urls)
            
    # 2. Scan screens table
    result_s = await db.execute(select(Screen))
    screens = result_s.scalars().all()
    for s in screens:
        if s.project_data:
            _extract_urls_from_json(s.project_data, urls)
            
    return urls

def _extract_urls_from_json(val, urls_set: set):
    if isinstance(val, dict):
        for k, v in val.items():
            _extract_urls_from_json(v, urls_set)
    elif isinstance(val, list):
        for item in val:
            _extract_urls_from_json(item, urls_set)
    elif isinstance(val, str):
        # Match potential relative or absolute resource links
        if val.startswith("/") or val.startswith("http://") or val.startswith("https://"):
            urls_set.add(val)
