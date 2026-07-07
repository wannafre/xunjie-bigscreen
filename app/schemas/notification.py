from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class NotificationBase(BaseModel):
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    type: str = Field(default="system", description="通知类型: system系统通知, message内部消息, todo待办事项")
    create_time: Optional[datetime] = Field(None, description="发送时间")
    expire_time: Optional[datetime] = Field(None, description="截止时间")

class NotificationCreate(NotificationBase):
    user_id: Optional[int] = Field(default=-1, description="接收用户 ID")

class NotificationUpdate(BaseModel):
    title: Optional[str] = Field(None)
    content: Optional[str] = Field(None)
    type: Optional[str] = Field(None)
    create_time: Optional[datetime] = Field(None)
    expire_time: Optional[datetime] = Field(None)

class NotificationOut(NotificationBase):
    id: int = Field(..., description="通知内容 ID")
    create_by: Optional[str] = Field(None, description="发布人")
    create_time: datetime = Field(..., description="发布时间")
    sys_create_time: datetime = Field(..., description="系统创建时间")
    
    # Read status details (linked to current recipient)
    user_id: Optional[int] = Field(None, description="接收用户 ID")
    is_read: int = Field(default=0, description="是否已读：0-未读, 1-已读")
    read_time: Optional[datetime] = Field(None, description="阅读时间")
    is_deleted: int = Field(default=0, description="用户是否删除（软删除）：0-正常, 1-已删")

    class Config:
        from_attributes = True

class NotificationReadUser(BaseModel):
    user_id: int = Field(..., description="用户 ID")
    username: str = Field(..., description="登录账号")
    nickname: str = Field(..., description="用户昵称")
    read_time: datetime = Field(..., description="阅读时间")
