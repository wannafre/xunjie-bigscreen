from typing import Any, Optional
from fastapi.responses import JSONResponse

# ==========================================
# Unified Response Codes (Business status codes)
# ==========================================
class ResponseCode:
    SUCCESS = 200                # 操作成功 (Success)
    
    # 鉴权与安全验证类 (400-499)
    UNAUTHORIZED = 401           # 身份验证失败/未登录 (Unauthorized)
    FORBIDDEN = 403              # 权限不足 (Forbidden)
    INVALID_CREDENTIALS = 40001  # 用户名或密码错误 (Invalid Credentials)
    CAPTCHA_REQUIRED = 42801     # 需要滑块验证码验证 (Captcha Challenge Required)
    INVALID_CAPTCHA = 42802      # 验证码失效或校验不通过 (Invalid or Expired Captcha)
    
    # 通用系统错误类 (500-599)
    ERROR = 500                  # 服务器内部错误 (Internal Server Error)

def make_response(
    status_code: int,
    code: int,
    message: str,
    data: Optional[Any] = None
) -> JSONResponse:
    """
    Returns a unified JSON response structure directly to avoid FastAPI's 
    default wrapping (e.g. nested inside a 'detail' object).
    
    Structure:
    {
        "code": "BUSINESS_CODE",
        "message": "User-friendly description",
        "data": null or payload
    }
    """
    return JSONResponse(
        status_code=status_code,
        content={
            "code": code,
            "message": message,
            "data": data
        }
    )
