import random
import string
import uuid
from typing import Optional
from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.core.captcha import captcha_manager, generate_captcha_images, decrypt_point_json

router = APIRouter()

# ==========================================
# Pydantic Schemas for Captcha
# ==========================================

class CaptchaGetRequest(BaseModel):
    captchaType: str = Field("blockPuzzle", description="验证码类型")

class CaptchaGetRepData(BaseModel):
    originalImageBase64: str
    jigsawImageBase64: str
    token: str
    secretKey: str
    result: bool = False
    opType: Optional[str] = None

class CaptchaGetResponse(BaseModel):
    repCode: str = "0000"
    repMsg: str = "success"
    repData: Optional[CaptchaGetRepData] = None

class CaptchaCheckRequest(BaseModel):
    captchaType: str = Field("blockPuzzle", description="验证码类型")
    pointJson: str = Field(..., description="AES加密后的坐标点数据")
    token: str = Field(..., description="验证码标识token")

class CaptchaCheckResponse(BaseModel):
    repCode: str
    repMsg: str

# ==========================================
# Captcha Router Endpoints
# ==========================================

@router.post("/get", response_model=CaptchaGetResponse)
async def get_captcha(data: CaptchaGetRequest) -> CaptchaGetResponse:
    """
    Get a new interactive sliding puzzle captcha challenge.
    """
    try:
        bg_base64, jigsaw_base64, target_x = generate_captcha_images()
        
        # Generate tracking token and random 16-character AES secret key
        token = str(uuid.uuid4()).replace("-", "")
        secret_key = "".join(random.choices(string.ascii_letters + string.digits, k=16))
        
        # Cache the target coordinates and AES key
        captcha_manager.create_token(token, target_x, secret_key, ttl=300)
        
        rep_data = CaptchaGetRepData(
            originalImageBase64=bg_base64,
            jigsawImageBase64=jigsaw_base64,
            token=token,
            secretKey=secret_key
        )
        return CaptchaGetResponse(repData=rep_data)
    except Exception as e:
        return CaptchaGetResponse(repCode="5000", repMsg=f"生成验证码失败: {str(e)}")

@router.post("/check", response_model=CaptchaCheckResponse)
async def check_captcha(data: CaptchaCheckRequest) -> CaptchaCheckResponse:
    """
    Validate the user's slide position (pointJson coordinates).
    """
    token_data = captcha_manager.get_token_data(data.token)
    if not token_data:
        return CaptchaCheckResponse(repCode="6111", repMsg="验证码已失效，请刷新")
    
    # Decrypt AES-encrypted pointJson
    point = decrypt_point_json(data.pointJson, token_data["secret_key"])
    if not point or "x" not in point:
        return CaptchaCheckResponse(repCode="6110", repMsg="坐标解析失败")
        
    slider_x = float(point["x"])
    target_x = float(token_data["target_x"])
    
    # Tolerance range of ±8 pixels
    if abs(slider_x - target_x) <= 8:
        captcha_manager.verify_token(data.token)
        return CaptchaCheckResponse(repCode="0000", repMsg="success")
    else:
        return CaptchaCheckResponse(repCode="6110", repMsg="验证失败")
