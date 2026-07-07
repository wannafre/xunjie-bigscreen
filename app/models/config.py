from sqlalchemy import Column, BigInteger, String, CHAR, DateTime, Text, func
from app.core.database import Base

class SystemConfig(Base):
    __tablename__ = "sys_config"
    __table_args__ = {"comment": "参数配置表"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键 ID")
    config_name = Column(String(100), nullable=False, default="", comment="配置名称")
    config_key = Column(String(100), nullable=False, unique=True, index=True, comment="配置键名")
    config_value = Column(Text, nullable=False, comment="配置键值")
    is_system = Column(CHAR(1), nullable=False, default="1", comment="是否系统内置（0否，1是）")
    remark = Column(String(500), nullable=True, default="", comment="备注信息")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=True, onupdate=func.now(), comment="更新时间")
