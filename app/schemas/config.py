from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class SystemConfigBase(BaseModel):
    config_name: str = Field(..., description="配置名称")
    config_key: str = Field(..., description="配置键名")
    config_value: str = Field(..., description="配置键值")
    is_system: Optional[str] = Field(default="1", description="是否系统内置（0否，1是）")
    remark: Optional[str] = Field(default="", description="备注信息")

class SystemConfigCreate(SystemConfigBase):
    pass

class SystemConfigUpdate(BaseModel):
    config_name: Optional[str] = Field(None, description="配置名称")
    config_value: Optional[str] = Field(None, description="配置键值")
    remark: Optional[str] = Field(None, description="备注信息")

class SystemConfigOut(SystemConfigBase):
    id: int = Field(..., description="主键 ID")
    create_time: datetime = Field(..., description="创建时间")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
