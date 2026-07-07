from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

class ScreenBase(BaseModel):
    name: str = Field(..., description="大屏项目名称")
    description: Optional[str] = Field(default="", description="项目描述")
    thumbnail: Optional[str] = Field(default="", description="缩略图路径/URL")
    project_data: Optional[Any] = Field(default=None, description="大屏设计配置JSON(画布大小、背景、图表位置等)")
    is_published: Optional[str] = Field(default="0", description="发布状态：0未发布，1已发布")

class ScreenCreate(ScreenBase):
    pass

class ScreenUpdate(BaseModel):
    name: Optional[str] = Field(None, description="大屏项目名称")
    description: Optional[str] = Field(None, description="项目描述")
    thumbnail: Optional[str] = Field(None, description="缩略图路径/URL")
    project_data: Optional[Any] = Field(None, description="大屏设计配置JSON")
    is_published: Optional[str] = Field(None, description="发布状态：0未发布，1已发布")

class ScreenOut(ScreenBase):
    id: int = Field(..., description="主键 ID")
    user_id: int = Field(..., description="所属用户ID")
    del_flag: str = Field(..., description="删除标志")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: datetime = Field(..., description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
