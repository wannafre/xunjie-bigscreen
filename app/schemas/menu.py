from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MenuBase(BaseModel):
    parent_id: int = Field(default=0, description="父菜单 ID")
    menu_name: str = Field(..., description="菜单名称")
    menu_type: str = Field(..., description="菜单类型：M (目录), C (菜单), F (按钮/接口)")
    order_num: Optional[int] = Field(default=0, description="显示顺序")
    path: Optional[str] = Field(default='', description="前端路由地址")
    component: Optional[str] = Field(default=None, description="前端组件路径")
    query_param: Optional[str] = Field(default=None, description="路由可选的默认传递参数")
    is_frame: Optional[int] = Field(default=0, description="是否为外链（0 否，1 是）")
    is_cache: Optional[int] = Field(default=0, description="是否缓存（0 缓存，1 不缓存）")
    visible: Optional[str] = Field(default='0', description="显示状态（0 显示，1 隐藏）")
    status: Optional[str] = Field(default='0', description="菜单状态（0 正常，1 停用）")
    perms: Optional[str] = Field(default=None, description="权限标识字符串")
    icon: Optional[str] = Field(default='#', description="菜单图标")
    remark: Optional[str] = Field(default='', description="备注信息")

class MenuCreate(MenuBase):
    pass

class MenuUpdate(BaseModel):
    parent_id: Optional[int] = None
    menu_name: Optional[str] = None
    menu_type: Optional[str] = None
    order_num: Optional[int] = None
    path: Optional[str] = None
    component: Optional[str] = None
    query_param: Optional[str] = None
    is_frame: Optional[int] = None
    is_cache: Optional[int] = None
    visible: Optional[str] = None
    status: Optional[str] = None
    perms: Optional[str] = None
    icon: Optional[str] = None
    remark: Optional[str] = None

class MenuOut(MenuBase):
    id: int
    create_time: datetime
    update_time: Optional[datetime] = None

    class Config:
        from_attributes = True

class MenuTree(MenuOut):
    children: list["MenuTree"] = []

MenuTree.model_rebuild()

