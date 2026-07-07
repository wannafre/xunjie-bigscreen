from sqlalchemy import Column, Integer, String, CHAR, SmallInteger, DateTime, text, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.role import role_menus

class Menu(Base):
    __tablename__ = "menus"
    __table_args__ = {"comment": "菜单权限表"}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True, comment="主键，自增 ID")
    parent_id = Column(Integer, nullable=False, default=0, comment="父菜单 ID（如果是顶级目录，则为 0）")
    menu_name = Column(String(50), nullable=False, comment="菜单/按钮的中文显示名称（如：用户管理）")
    menu_type = Column(CHAR(1), nullable=False, comment="菜单类型：M (目录), C (菜单), F (按钮/接口)")
    order_num = Column(Integer, nullable=True, default=0, comment="显示顺序（同级菜单升序排列，数字越小越靠前）")
    path = Column(String(200), nullable=True, default='', comment="前端路由地址（如：user，仅 M 和 C 类型需要）")
    component = Column(String(255), nullable=True, default=None, comment="前端组件路径（如：system/user/index，仅 C 类型菜单需要）")
    query_param = Column(String(255), nullable=True, default=None, comment="路由可选的默认传递参数（JSON 字符串，如 {\"id\": 1}）")
    is_frame = Column(SmallInteger, nullable=True, default=0, comment="是否为外链（0 否，1 是。如果是外链，点击会新窗口打开 path）")
    is_cache = Column(SmallInteger, nullable=True, default=0, comment="是否缓存（0 缓存，1 不缓存。对应 Vue 的 Keep-Alive）")
    visible = Column(CHAR(1), nullable=True, default='0', comment="显示状态（0 显示，1 隐藏。隐藏后菜单栏看不见，但路由仍有效）")
    status = Column(CHAR(1), nullable=True, default='0', comment="菜单状态（0 正常，1 停用。停用后整个菜单及其子节点全部失效）")
    perms = Column(String(100), nullable=True, default=None, comment="权限标识字符串（如 system:user:add，后端鉴权的核心凭证）")
    icon = Column(String(100), nullable=True, default='#', comment="菜单图标（通常存 Element Plus 的图标名，如 User, Setting）")
    remark = Column(String(500), nullable=True, default='', comment="备注信息")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_time = Column(DateTime, nullable=True, onupdate=func.now(), comment="更新时间")


    # Relationships
    roles = relationship("Role", secondary=role_menus, back_populates="menus")
