from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import Optional
import logging
from datetime import datetime, timedelta
from app.core.config import settings

from app.models.user import User
from app.models.role import Role
from app.models.menu import Menu
from app.crud.user import get_user_by_username, create_user
from app.schemas.user import UserCreate
from app.core.security import verify_password

logger = logging.getLogger(__name__)

async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
    """
    Authenticate a user by checking username and password hash.
    """
    user = await get_user_by_username(db, username)
    if not user:
        return None
    if not verify_password(password, user.password, user.salt):
        return None
    return user

from app.models.dict import DictType, DictData

async def seed_default_users(db: AsyncSession) -> None:
    """
    Seeds default menus, buttons, roles, dicts, and admin/editor accounts if they don't already exist.
    """
    try:
        # 1. 确保顶级目录 "系统信息管理" 存在
        res_p = await db.execute(select(Menu).filter(Menu.menu_type == "M", Menu.path == "system"))
        system_cat = res_p.scalars().first()
        if not system_cat:
            system_cat = Menu(
                menu_name="系统信息管理",
                menu_type="M",
                order_num=10,
                path="system",
                icon="Setting",
                status="0",
                visible="0"
            )
            db.add(system_cat)
            await db.commit()
            await db.refresh(system_cat)
        p_id = system_cat.id

        # 2. 确保核心菜单存在
        menu_items = [
            # {"name": "个人账号信息维护", "perms": None, "path": "account", "order": 11, "icon": "User"},
            {"name": "用户管理", "perms": "system:user:list", "path": "user", "order": 12, "icon": "Avatar"},
            {"name": "角色管理", "perms": "system:role:list", "path": "role", "order": 13, "icon": "Key"},
            {"name": "菜单管理", "perms": "system:menu:list", "path": "menu", "order": 15, "icon": "Setting"},
            {"name": "字典管理", "perms": "system:dict:list", "path": "dictionary", "order": 16, "icon": "Notebook"},
            {"name": "通知管理", "perms": "system:notification:list", "path": "notification", "order": 17, "icon": "Bell"},
        ]
        
        menus_by_name = {}
        for item in menu_items:
            res = await db.execute(select(Menu).filter(Menu.menu_name == item["name"], Menu.menu_type == "C"))
            menu_obj = res.scalars().first()
            if not menu_obj:
                menu_obj = Menu(
                    menu_name=item["name"],
                    menu_type="C",
                    perms=item["perms"],
                    path=item["path"] if p_id == 0 else f"system/{item['path']}",
                    component=f"system/{item['path']}/index.vue" if p_id != 0 else None,
                    order_num=item["order"],
                    parent_id=p_id,
                    status="0",
                    visible="0",
                    icon=item.get("icon", "#")
                )
                db.add(menu_obj)
                await db.commit()
                await db.refresh(menu_obj)
            else:
                # Self-healing: if parent_id is 0 and system_cat exists, nest it correctly
                is_changed = False
                if menu_obj.parent_id == 0 and p_id != 0:
                    menu_obj.parent_id = p_id
                    menu_obj.path = f"system/{item['path']}"
                    menu_obj.component = f"system/{item['path']}/index.vue"
                    is_changed = True
                if menu_obj.icon != item.get("icon", "#"):
                    menu_obj.icon = item.get("icon", "#")
                    is_changed = True
                if is_changed:
                    db.add(menu_obj)
                    await db.commit()
                    await db.refresh(menu_obj)
            menus_by_name[item["name"]] = menu_obj

        # 3. 确保各菜单下的按钮/接口权限存在
        button_definitions = {
            "用户管理": [
                {"name": "用户查询", "perms": "system:user:query"},
                {"name": "用户新增", "perms": "system:user:add"},
                {"name": "用户修改", "perms": "system:user:edit"},
                {"name": "用户删除", "perms": "system:user:remove"},
                {"name": "重置密码", "perms": "system:user:resetPwd"},
            ],
            "角色管理": [
                {"name": "角色查询", "perms": "system:role:query"},
                {"name": "角色新增", "perms": "system:role:add"},
                {"name": "角色修改", "perms": "system:role:edit"},
                {"name": "角色删除", "perms": "system:role:remove"},
            ],
            "菜单管理": [
                {"name": "菜单查询", "perms": "system:menu:query"},
                {"name": "菜单新增", "perms": "system:menu:add"},
                {"name": "菜单修改", "perms": "system:menu:edit"},
                {"name": "菜单删除", "perms": "system:menu:remove"},
            ],
            "字典管理": [
                {"name": "字典查询", "perms": "system:dict:query"},
                {"name": "字典新增", "perms": "system:dict:add"},
                {"name": "字典修改", "perms": "system:dict:edit"},
                {"name": "字典删除", "perms": "system:dict:remove"},
            ],
            "通知管理": [
                {"name": "通知查询", "perms": "system:notification:list"},
                {"name": "通知新增", "perms": "system:notification:add"},
                {"name": "通知修改", "perms": "system:notification:edit"},
                {"name": "通知删除", "perms": "system:notification:remove"},
            ],
        }

        for parent_name, buttons in button_definitions.items():
            if parent_name not in menus_by_name:
                continue
            parent_menu = menus_by_name[parent_name]
            for btn in buttons:
                res = await db.execute(
                    select(Menu).filter(Menu.perms == btn["perms"], Menu.parent_id == parent_menu.id)
                )
                btn_obj = res.scalars().first()
                if not btn_obj:
                    btn_obj = Menu(
                        menu_name=btn["name"],
                        menu_type="F",
                        perms=btn["perms"],
                        parent_id=parent_menu.id,
                        status="0",
                        visible="0",
                        order_num=0
                    )
                    db.add(btn_obj)
        await db.commit()

        # 获取当前所有的 Menu 记录以分配给 admin
        res_all_menus = await db.execute(select(Menu))
        all_menus = res_all_menus.scalars().all()

        # 4. 种子初始化角色，并建立角色-菜单关联
        res_roles = await db.execute(select(Role))
        all_roles = res_roles.scalars().all()
        admin_role = None
        editor_role = None
        
        if not all_roles:
            admin_role = Role(role_name="管理员", role_key="admin", status="0")
            editor_role = Role(role_name="编辑者", role_key="editor", status="0")
            
            # 管理员角色关联全部菜单/按钮权限
            admin_role.menus = all_menus
            
            # 编辑者角色关联账号、菜单和通知管理
            editor_menus = [m for m in all_menus if m.path in ["system/account", "system/menu", "system/notification", "system"] or m.perms in ["system:menu:query", "system:notification:list"]]
            editor_role.menus = editor_menus
                
            db.add(admin_role)
            db.add(editor_role)
            await db.commit()
            await db.refresh(admin_role)
            await db.refresh(editor_role)
            logger.info("Default roles seeded successfully.")
        else:
            admin_role = [r for r in all_roles if r.role_key == "admin"][0]
            # 确保管理员拥有所有最新菜单/按钮的关联
            admin_role.menus = all_menus
            db.add(admin_role)
            
            editor_role = [r for r in all_roles if r.role_key == "editor"]
            if editor_role:
                # 确保编辑者关联最新的账号、菜单和通知管理
                editor_menus = [m for m in all_menus if m.path in ["system/account", "system/menu", "system/notification", "system"] or m.perms in ["system:menu:query", "system:notification:list"]]
                editor_role[0].menus = editor_menus
                db.add(editor_role[0])
            await db.commit()

        # 4. 种子初始化系统默认用户，并绑定角色
        admin_user = await get_user_by_username(db, "admin")
        if not admin_user:
            admin_in = UserCreate(
                username="admin",
                nickname="超级管理员",
                password="123456",
                roles=["admin"],
                avatar="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
                remark="I am a super administrator"
            )
            await create_user(db, admin_in)
            logger.info("Default 'admin' user created successfully.")

        editor_user = await get_user_by_username(db, "editor")
        if not editor_user:
            editor_in = UserCreate(
                username="editor",
                nickname="普通编辑员",
                password="123456",
                roles=["editor"],
                avatar="https://wpimg.wallstcn.com/f778738c-e4f8-4870-b634-56703b4acafe.gif",
                remark="I am an editor"
            )
            await create_user(db, editor_in)
            logger.info("Default 'editor' user created successfully.")
            
        # 5. 种子初始化字典类型与数据
        res_dict = await db.execute(select(DictType))
        all_dicts = res_dict.scalars().all()
        if not all_dicts:
            dict_types = [
                DictType(dict_name="用户性别", dict_type="sys_user_sex", status="0", remark="用户性别列表"),
                DictType(dict_name="系统状态", dict_type="sys_normal_disable", status="0", remark="系统正常/停用状态列表")
            ]
            db.add_all(dict_types)
            await db.commit()
            
            dict_datas = [
                DictData(dict_sort=1, dict_label="男", dict_value="0", dict_type="sys_user_sex", list_class="primary", is_default="Y", status="0"),
                DictData(dict_sort=2, dict_label="女", dict_value="1", dict_type="sys_user_sex", list_class="danger", is_default="N", status="0"),
                DictData(dict_sort=3, dict_label="未知", dict_value="2", dict_type="sys_user_sex", list_class="info", is_default="N", status="0"),
                
                DictData(dict_sort=1, dict_label="正常", dict_value="0", dict_type="sys_normal_disable", list_class="primary", is_default="Y", status="0"),
                DictData(dict_sort=2, dict_label="停用", dict_value="1", dict_type="sys_normal_disable", list_class="danger", is_default="N", status="0")
            ]
            db.add_all(dict_datas)
            await db.commit()
            logger.info("Default dictionary types and data seeded successfully.")
            
            # 6. 种子初始化通知数据
            from app.models.notification import Notification, UserNotification
            res_notices = await db.execute(select(Notification))
            all_notices = res_notices.scalars().all()
            if not all_notices:
                admin_user = await get_user_by_username(db, "admin")
                editor_user = await get_user_by_username(db, "editor")
                
                # Mock notifications data
                notices_to_create = []
                if admin_user:
                    notices_to_create.append(
                        {"user_id": admin_user.id, "title": "系统升级通知", "content": "尊敬的超级管理员，系统已成功升级至 V1.0.0 版本。本次更新优化了个人账号管理、路由菜单架构，并全新上线了通知管理功能。", "type": "system", "is_read": 0}
                    )
                    notices_to_create.append(
                        {"user_id": admin_user.id, "title": "安全警报：异地登录提醒", "content": "您的账号于今日在未知 IP 登录，请确认是否为本人操作。如非本人操作，请及时前往个人中心修改密码。", "type": "message", "is_read": 0}
                    )
                    notices_to_create.append(
                        {"user_id": admin_user.id, "title": "待处理任务：审核权限申请", "content": "您有一条新的审核任务：普通编辑员（editor）提交了关于“系统字典修改”权限的审批申请，请及时前往处理。", "type": "todo", "is_read": 0}
                    )
                    notices_to_create.append(
                        {"user_id": admin_user.id, "title": "欢迎加入迅捷系统", "content": "欢迎使用迅捷后台管理系统！这是一个基于 FastAPI 与 Vue 3 构建的轻量级开发框架。", "type": "system", "is_read": 1}
                    )
                if editor_user:
                    notices_to_create.append(
                        {"user_id": editor_user.id, "title": "账号开通成功", "content": "您的编辑员账号已开通，分配角色为“编辑者”。请按规定开展内容维护工作。", "type": "system", "is_read": 0}
                    )
                    notices_to_create.append(
                        {"user_id": editor_user.id, "title": "待办：完善个人基本资料", "content": "请及时进入“个人账号信息维护”页面，完善您的手机号码、电子邮箱等联系信息。", "type": "todo", "is_read": 0}
                    )
                
                for item in notices_to_create:
                    # 1. Add notification content
                    notif = Notification(
                        title=item["title"],
                        content=item["content"],
                        type=item["type"],
                        create_by="admin"
                    )
                    db.add(notif)
                    await db.commit()
                    await db.refresh(notif)
                    
                    # 2. Add user read state
                    user_notif = UserNotification(
                        user_id=item["user_id"],
                        notification_id=notif.id,
                        is_read=item["is_read"],
                        read_time=settings.get_current_time() if item["is_read"] == 1 else None
                    )
                    db.add(user_notif)
                    await db.commit()
                
                logger.info("Default notifications and user read states seeded successfully.")
            
    except Exception as e:
        logger.error(f"Error seeding default users, roles, and menus: {e}")


