from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

# Dict Type Schemas
class DictTypeBase(BaseModel):
    dict_name: str = Field(..., description="字典分类名称")
    dict_type: str = Field(..., description="字典类型全局唯一标识")
    status: Optional[str] = Field(default="0", description="状态（0 正常，1 停用）")
    remark: Optional[str] = Field(default="", description="备注信息")

class DictTypeCreate(DictTypeBase):
    pass

class DictTypeUpdate(BaseModel):
    dict_name: Optional[str] = None
    dict_type: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None

class DictTypeOut(DictTypeBase):
    dict_id: int
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True


# Dict Data Schemas
class DictDataBase(BaseModel):
    dict_sort: Optional[int] = Field(default=0, description="显示顺序")
    dict_label: str = Field(..., description="字典标签（如：男、女）")
    dict_value: str = Field(..., description="字典键值（如：0、1）")
    dict_type: str = Field(..., description="字典类型（关联 dict_types.dict_type）")
    css_class: Optional[str] = Field(default=None, description="样式属性")
    list_class: Optional[str] = Field(default=None, description="表格回显样式（如: primary, success, info, warning, danger）")
    is_default: Optional[str] = Field(default="N", description="是否默认（Y 是，N 否）")
    status: Optional[str] = Field(default="0", description="状态（0 正常，1 停用）")
    remark: Optional[str] = Field(default="", description="备注信息")

class DictDataCreate(DictDataBase):
    pass

class DictDataUpdate(BaseModel):
    dict_sort: Optional[int] = None
    dict_label: Optional[str] = None
    dict_value: Optional[str] = None
    dict_type: Optional[str] = None
    css_class: Optional[str] = None
    list_class: Optional[str] = None
    is_default: Optional[str] = None
    status: Optional[str] = None
    remark: Optional[str] = None

class DictDataOut(DictDataBase):
    dict_code: int
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True
