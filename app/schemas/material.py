from pydantic import BaseModel, Field, model_validator
from typing import Optional, Any
from datetime import datetime

class MaterialBase(BaseModel):
    name: str = Field(..., description="素材名称")
    category: str = Field(..., description="大类：background, echarts, decoration, geojson等")
    subcategory: Optional[str] = Field(default="", description="子类：bar, line, pie, map, image等")
    thumbnail: Optional[str] = Field(default="", description="缩略图路径/URL")
    config_data: Optional[Any] = Field(default=None, description="核心配置JSON(ECharts Option, 样式参数等)")
    is_official: Optional[bool] = Field(default=False, description="是否为官方预设素材")

class MaterialCreate(MaterialBase):
    creator_id: Optional[int] = Field(default=None, description="创建者用户ID")
    parent_id: Optional[int] = Field(default=None, description="克隆自官方素材的ID")

class MaterialUpdate(BaseModel):
    name: Optional[str] = Field(None, description="素材名称")
    category: Optional[str] = Field(None, description="大类")
    subcategory: Optional[str] = Field(None, description="子类")
    thumbnail: Optional[str] = Field(None, description="缩略图路径/URL")
    config_data: Optional[Any] = Field(None, description="核心配置JSON")
    is_official: Optional[bool] = Field(None, description="是否官方")
    parent_id: Optional[int] = Field(None, description="克隆父级素材ID")

class MaterialOut(MaterialBase):
    id: int = Field(..., description="主键 ID")
    creator_id: Optional[int] = Field(None, description="创建者用户ID")
    parent_id: Optional[int] = Field(None, description="克隆自官方素材的ID")
    del_flag: str = Field(..., description="删除标志")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: datetime = Field(..., description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")

    @model_validator(mode="after")
    def sign_resource_urls(self):
        from app.services.signature_service import LocalPresignedUrlManager
        
        # 1. Sign thumbnail
        if self.thumbnail and not self.thumbnail.startswith(("http://", "https://", "data:", "blob:")):
            self.thumbnail = LocalPresignedUrlManager.generate_presigned_url(self.thumbnail)
            
        # 2. Sign config_data recursively
        if self.config_data:
            self.config_data = LocalPresignedUrlManager.sign_urls_in_json(self.config_data)
                
        return self

    class Config:
        from_attributes = True

from app.schemas.common import PageResult

class MaterialPaginationOut(PageResult[MaterialOut]):
    pass
