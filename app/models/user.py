from sqlalchemy import Column, Integer, BigInteger, String, CHAR, DateTime, func
from sqlalchemy.orm import relationship
from app.core.database import Base
from app.models.role import user_roles

class User(Base):
    __tablename__ = "users"
    __table_args__ = {"comment": "用户信息表"}

    id = Column(BigInteger, primary_key=True, index=True, autoincrement=True, comment="主键 ID")
    dept_id = Column(BigInteger, nullable=True, default=None, comment="部门 ID")
    username = Column(String(30), unique=True, index=True, nullable=False, comment="登录账号")
    nickname = Column(String(30), nullable=False, comment="用户昵称")
    user_type = Column(String(2), nullable=True, default="00", comment="用户类型：00系统内置员工，01注册会员，02外部协作者")
    email = Column(String(50), nullable=True, default="", comment="用户邮箱")
    phonenumber = Column(String(11), nullable=True, default="", comment="手机号码")
    sex = Column(CHAR(1), nullable=True, default="0", comment="用户性别：0男，1女，2未知")
    avatar = Column(String(255), nullable=True, default="", comment="头像服务器路径")
    password = Column(String(100), nullable=False, comment="密码密文")
    status = Column(CHAR(1), nullable=False, default="0", comment="帐号状态：0正常，1停用")
    del_flag = Column(CHAR(1), nullable=False, default="0", comment="删除标志：0代表存在，2代表删除")
    login_ip = Column(String(128), nullable=True, default="", comment="最后登录 IP")
    login_date = Column(DateTime, nullable=True, default=None, comment="最后登录时间")
    pwd_update_date = Column(DateTime, nullable=True, default=None, comment="密码最后修改时间")
    login_retry = Column(Integer, nullable=False, default=0, comment="连续输错密码次数")
    remark = Column(String(500), nullable=True, default="", comment="备注信息")
    create_by = Column(String(64), nullable=True, default="", comment="创建者")
    create_time = Column(DateTime, nullable=False, server_default=func.now(), comment="创建时间")
    update_by = Column(String(64), nullable=True, default="", comment="更新者")
    update_time = Column(DateTime, nullable=True, onupdate=func.now(), comment="更新时间")
    
    salt = Column(String(50), nullable=False, default="", comment="密码盐")

    # Many-to-Many Relationship with Role
    roles = relationship("Role", secondary=user_roles, back_populates="users", lazy="selectin")

    @property
    def permissions(self) -> list:
        """
        Dynamically aggregate all unique active permission strings (perms) 
        from the user's active roles and menus.
        """
        if self.username == "admin":
            return ["*:*:*"]
        perms = set()
        for role in self.roles:
            if role.status == "0":
                for menu in role.menus:
                    if menu.status == "0" and menu.perms:
                        perms.add(menu.perms)
        return list(perms)

