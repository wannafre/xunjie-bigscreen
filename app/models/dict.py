from sqlalchemy import Column, Integer, BigInteger, String, CHAR, DateTime, func
from app.core.database import Base

class DictType(Base):
    __tablename__ = "dict_types"
    __table_args__ = {"comment": "字典类型表"}

    dict_id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键，自增 ID")
    dict_name = Column(String(100), nullable=False, default="", comment="字典分类名称（如：用户性别、设备状态）")
    dict_type = Column(String(100), nullable=False, unique=True, index=True, comment="字典类型全局唯一标识（如：sys_user_sex，全表唯一索引 UNIQUE）")
    status = Column(CHAR(1), nullable=True, default="0", comment="状态（0 正常，1 停用）")
    remark = Column(String(500), nullable=True, default="", comment="备注信息（详细说明这个字典是用在哪个模块的）")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=True, onupdate=func.now(), comment="更新时间")


class DictData(Base):
    __tablename__ = "dict_data"
    __table_args__ = {"comment": "字典数据表"}

    dict_code = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键，自增 ID")
    dict_sort = Column(Integer, nullable=True, default=0, comment="显示顺序")
    dict_label = Column(String(100), nullable=False, default="", comment="字典标签（如：男、女）")
    dict_value = Column(String(100), nullable=False, default="", comment="字典键值（如：0、1）")
    dict_type = Column(String(100), nullable=False, index=True, comment="字典类型全局唯一标识（关联 dict_types.dict_type）")
    css_class = Column(String(100), nullable=True, default=None, comment="样式属性（其他样式扩展）")
    list_class = Column(String(100), nullable=True, default=None, comment="表格回显样式（如: primary, success, info, warning, danger）")
    is_default = Column(CHAR(1), nullable=True, default="N", comment="是否默认（Y 是，N 否）")
    status = Column(CHAR(1), nullable=True, default="0", comment="状态（0 正常，1 停用）")
    remark = Column(String(500), nullable=True, default="", comment="备注信息")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=True, onupdate=func.now(), comment="更新时间")
