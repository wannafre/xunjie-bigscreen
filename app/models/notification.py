from sqlalchemy import Column, BigInteger, String, Text, DateTime, SmallInteger, func, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = {"comment": "系统通知内容表"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键 ID")
    title = Column(String(100), nullable=False, comment="通知标题")
    content = Column(Text, nullable=False, comment="通知内容")
    type = Column(String(20), nullable=False, default="system", comment="通知类型: system系统通知, message内部消息, todo待办事项")
    create_by = Column(String(64), nullable=True, comment="创建人/发布人")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="发布时间")
    expire_time = Column(DateTime, nullable=True, comment="截止时间/失效时间")
    sys_create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="系统创建时间")

    # Relationship to user read states
    read_states = relationship("UserNotification", back_populates="notification", cascade="all, delete-orphan")


class UserNotification(Base):
    __tablename__ = "user_notifications"
    __table_args__ = {"comment": "用户通知阅读表"}

    id = Column(BigInteger, primary_key=True, autoincrement=True, comment="主键 ID")
    user_id = Column(BigInteger, nullable=False, index=True, comment="接收用户 ID")
    notification_id = Column(BigInteger, ForeignKey("notifications.id"), nullable=False, index=True, comment="通知内容 ID")
    is_read = Column(SmallInteger, nullable=False, default=0, comment="是否已读：0-未读, 1-已读")
    read_time = Column(DateTime, nullable=True, default=None, comment="阅读时间")
    is_deleted = Column(SmallInteger, nullable=False, default=0, comment="用户是否删除（软删除）：0-正常, 1-已删")

    # Relationship to notification content
    notification = relationship("Notification", back_populates="read_states")
