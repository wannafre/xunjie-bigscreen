from sqlalchemy import Column, BigInteger, String, CHAR, DateTime, JSON, ForeignKey, Boolean, func
from sqlalchemy.orm import relationship
from app.core.database import Base

class Material(Base):
    __tablename__ = "materials"
    __table_args__ = {"comment": "图表与素材模板表"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键 ID")
    name = Column(String(100), nullable=False, comment="素材名称")
    category = Column(String(50), nullable=False, index=True, comment="大类：background, echarts, decoration, geojson等")
    subcategory = Column(String(50), nullable=True, default="", comment="子类：bar, line, pie, map, image等")
    thumbnail = Column(String(255), nullable=True, default="", comment="缩略图路径/URL")
    config_data = Column(JSON, nullable=True, comment="核心配置JSON(ECharts Option, 样式参数等)")
    is_official = Column(Boolean, nullable=False, default=False, comment="是否为官方预设素材")
    creator_id = Column(BigInteger, ForeignKey("users.id"), nullable=True, index=True, comment="创建者用户ID")
    parent_id = Column(BigInteger, ForeignKey("materials.id"), nullable=True, comment="克隆自官方素材的ID")
    del_flag = Column(CHAR(1), nullable=False, default="0", comment="删除标志：0存在，2删除")
    create_by = Column(String(64), nullable=True, default="", comment="创建者")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_by = Column(String(64), nullable=True, default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, onupdate=func.now(), comment="更新时间")

    # Relationships
    creator = relationship("User", backref="created_materials")
    parent = relationship("Material", remote_side=[id], backref="cloned_materials")
