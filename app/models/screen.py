from sqlalchemy import Column, BigInteger, String, CHAR, DateTime, JSON, ForeignKey, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Screen(Base):
    __tablename__ = "screens"
    __table_args__ = {"comment": "大屏可视化项目表"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键 ID")
    name = Column(String(100), nullable=False, comment="大屏项目名称")
    description = Column(String(500), nullable=True, default="", comment="项目描述")
    thumbnail = Column(String(255), nullable=True, default="", comment="缩略图路径/URL")
    project_data = Column(JSON, nullable=True, comment="大屏设计配置JSON(画布大小、背景、图表位置和配置等)")
    is_published = Column(CHAR(1), nullable=False, default="0", comment="发布状态：0未发布，1已发布")
    user_id = Column(BigInteger, ForeignKey("users.id"), nullable=False, index=True, comment="所属用户ID")
    del_flag = Column(CHAR(1), nullable=False, default="0", comment="删除标志：0存在，2删除")
    create_by = Column(String(64), nullable=True, default="", comment="创建者")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_by = Column(String(64), nullable=True, default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, onupdate=func.now(), comment="更新时间")

    # Relationship to user
    user = relationship("User", backref="screens")
