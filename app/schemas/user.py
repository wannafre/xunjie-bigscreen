from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., description="登录账号")
    nickname: str = Field(..., description="用户昵称")
    dept_id: Optional[int] = Field(default=None, description="部门 ID")
    user_type: Optional[str] = Field(default="00", description="用户类型：00系统内置员工，01注册会员，02外部协作者")
    email: Optional[str] = Field(default="", description="用户邮箱")
    phonenumber: Optional[str] = Field(default="", description="手机号码")
    sex: Optional[str] = Field(default="0", description="用户性别：0男，1女，2未知")
    avatar: Optional[str] = Field(default="", description="头像服务器路径")
    status: Optional[str] = Field(default="0", description="帐号状态：0正常，1停用")
    remark: Optional[str] = Field(default="", description="备注信息")

class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="密码")
    roles: List[str] = Field(default=["user"], description="用户角色")
    salt: Optional[str] = Field(default=None, description="加密盐")

class UserUpdate(BaseModel):
    nickname: Optional[str] = Field(None, description="用户昵称")
    dept_id: Optional[int] = Field(None, description="部门 ID")
    user_type: Optional[str] = Field(None, description="用户类型")
    email: Optional[str] = Field(None, description="用户邮箱")
    phonenumber: Optional[str] = Field(None, description="手机号码")
    sex: Optional[str] = Field(None, description="用户性别")
    avatar: Optional[str] = Field(None, description="头像服务器路径")
    status: Optional[str] = Field(None, description="帐号状态")
    password: Optional[str] = Field(None, min_length=6, description="新密码")
    roles: Optional[List[str]] = Field(None, description="用户角色")
    remark: Optional[str] = Field(None, description="备注信息")

class UserOut(UserBase):
    id: int = Field(..., description="主键 ID")
    del_flag: str = Field(..., description="删除标志")
    login_ip: Optional[str] = Field(None, description="最后登录 IP")
    login_date: Optional[datetime] = Field(None, description="最后登录时间")
    pwd_update_date: Optional[datetime] = Field(None, description="密码最后修改时间")
    login_retry: int = Field(..., description="连续输错密码次数")
    create_by: Optional[str] = Field(None, description="创建者")
    create_time: datetime = Field(..., description="创建时间")
    update_by: Optional[str] = Field(None, description="更新者")
    update_time: Optional[datetime] = Field(None, description="更新时间")
    roles: List[str] = Field(default=[], description="用户角色")
    permissions: List[str] = Field(default=[], description="用户权限标识列表")

    @field_validator("roles", mode="before")
    @classmethod
    def serialize_roles(cls, v):
        if isinstance(v, list) and len(v) > 0 and not isinstance(v[0], str):
            return [role.role_key for role in v]
        return v

    class Config:
        from_attributes = True


class UserProfileUpdate(BaseModel):
    nickname: Optional[str] = Field(None, description="用户昵称")
    email: Optional[str] = Field(None, description="用户邮箱")
    phonenumber: Optional[str] = Field(None, description="手机号码")
    sex: Optional[str] = Field(None, description="用户性别")


class UserPasswordUpdate(BaseModel):
    old_password: str = Field(..., description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")


