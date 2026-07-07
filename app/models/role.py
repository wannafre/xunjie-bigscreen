from sqlalchemy import Column, Integer, BigInteger, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base

# Association Table for User <-> Role (Many-to-Many)
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", BigInteger, ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True)
)


# Association Table for Role <-> Menu (Many-to-Many)
role_menus = Table(
    "role_menus",
    Base.metadata,
    Column("role_id", Integer, ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("menu_id", Integer, ForeignKey("menus.id", ondelete="CASCADE"), primary_key=True)
)

class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    role_name = Column(String(50), nullable=False)  # Role display name (e.g. "管理员")
    role_key = Column(String(50), unique=True, index=True, nullable=False)  # Role key identifier (e.g. "admin")
    status = Column(String(1), nullable=False, default="0")  # Status (0: normal, 1: disabled)

    # Relationships
    users = relationship("User", secondary=user_roles, back_populates="roles")
    menus = relationship("Menu", secondary=role_menus, back_populates="roles", lazy="selectin")
