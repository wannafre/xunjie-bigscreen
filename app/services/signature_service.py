import time
import hmac
import hashlib
from app.core.config import settings

class LocalPresignedUrlManager:
    @staticmethod
    def generate_presigned_url(relative_path: str, expires_in_seconds: int = 7200) -> str:
        """
        生成带有时间效力和安全签名的本地文件读取链接
        默认有效期：2小时 (7200秒)
        """
        if not relative_path:
            return ""
            
        # 统一清理路径开头斜杠
        clean_path = relative_path.lstrip("/")
        
        # 避免重复签名
        if "api/v1/materials/files/view" in clean_path:
            return relative_path

        expires = int(time.time()) + expires_in_seconds
        
        # 计算签名
        string_to_sign = f"{clean_path}:{expires}"
        signature = hmac.new(
            settings.SECRET_KEY.encode('utf-8'),
            string_to_sign.encode('utf-8'),
            digestmod=hashlib.sha256
        ).hexdigest()
        
        # 生成带参数的 API 接口 URL
        return f"{settings.API_V1_STR}/materials/files/view?path={clean_path}&expires={expires}&signature={signature}"

    @classmethod
    def sign_urls_in_json(cls, data):
        """
        递归遍历并签名 JSON 数据中所有的 uploads 相对路径
        """
        if isinstance(data, dict):
            return {k: cls.sign_urls_in_json(v) for k, v in data.items()}
        elif isinstance(data, list):
            return [cls.sign_urls_in_json(item) for item in data]
        elif isinstance(data, str):
            clean = data.lstrip("/")
            if clean.startswith("uploads/") and "api/v1/materials/files/view" not in clean:
                if "?" not in clean:
                    return cls.generate_presigned_url(data)
            return data
        else:
            return data

