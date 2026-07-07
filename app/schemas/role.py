from pydantic import BaseModel, Field
from typing import List, Optional
from app.schemas.menu import MenuOut

class RoleBase(BaseModel):
    role_name: str = Field(..., description="角色名称")
    role_key: str = Field(..., description="角色权限字符")
    status: Optional[str] = Field(default="0", description="角色状态（0正常 1停用）")

class RoleCreate(RoleBase):
    menu_ids: Optional[List[int]] = Field(default=[], description="绑定的菜单 ID 列表")

class RoleUpdate(BaseModel):
    role_name: Optional[str] = None
    role_key: Optional[str] = None
    status: Optional[str] = None
    menu_ids: Optional[List[int]] = None

class RoleOut(RoleBase):
    id: int
    menus: List[MenuOut] = []

    class Config:
        from_attributes = True
        # Support computed string list for easy frontend usage
        @classmethod
        def compute_roles(cls, obj) -> str:
            return obj.role_key
