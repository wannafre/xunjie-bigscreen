from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user, check_permissions
from app.schemas.menu import MenuCreate, MenuUpdate, MenuOut, MenuTree
from app.crud import menu as crud_menu

router = APIRouter()

def build_tree(menus: list) -> List[MenuTree]:
    """
    Constructs the tree structure from a flat list of menus.
    """
    # Create MenuTree Pydantic objects first
    menu_map = {
        m.id: MenuTree(
            id=m.id,
            parent_id=m.parent_id,
            menu_name=m.menu_name,
            menu_type=m.menu_type,
            order_num=m.order_num,
            path=m.path,
            component=m.component,
            query_param=m.query_param,
            is_frame=m.is_frame,
            is_cache=m.is_cache,
            visible=m.visible,
            status=m.status,
            perms=m.perms,
            icon=m.icon,
            remark=m.remark,
            create_time=m.create_time,
            update_time=m.update_time,
            children=[]
        )
        for m in menus
    }
    
    tree = []
    # Build hierarchy using the mapped Pydantic objects
    for m in menus:
        node = menu_map[m.id]
        if m.parent_id == 0:
            tree.append(node)
        else:
            parent_node = menu_map.get(m.parent_id)
            if parent_node is not None:
                parent_node.children.append(node)
            else:
                # If parent not found (e.g. parent is deleted or filtered out), treat as root
                tree.append(node)
                
    return tree

@router.post("/", response_model=MenuOut, status_code=status.HTTP_201_CREATED)
async def create_menu_endpoint(
    menu_in: MenuCreate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(check_permissions("system:menu:add"))
):
    """
    Create a new menu.
    """
    return await crud_menu.create_menu(db, menu_in)

@router.get("/", response_model=List[MenuOut])
async def list_menus_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Get flat list of all menus.
    """
    return await crud_menu.get_all_menus(db)

@router.get("/tree", response_model=List[MenuTree])
async def get_menu_tree_endpoint(
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Get menus structured as a tree.
    """
    menus = await crud_menu.get_all_menus(db)
    return build_tree(menus)

@router.get("/{menu_id}", response_model=MenuOut)
async def get_menu_endpoint(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    """
    Get details of a specific menu.
    """
    menu = await crud_menu.get_menu_by_id(db, menu_id)
    if not menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )
    return menu

@router.put("/{menu_id}", response_model=MenuOut)
async def update_menu_endpoint(
    menu_id: int,
    menu_in: MenuUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(check_permissions("system:menu:edit"))
):
    """
    Update a menu.
    """
    db_menu = await crud_menu.get_menu_by_id(db, menu_id)
    if not db_menu:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Menu not found"
        )
    return await crud_menu.update_menu(db, db_menu, menu_in)

@router.delete("/{menu_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_menu_endpoint(
    menu_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: str = Depends(check_permissions("system:menu:remove"))
):
    """
    Delete a menu.
    """
    try:
        success = await crud_menu.delete_menu(db, menu_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Menu not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    return None

