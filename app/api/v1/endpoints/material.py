from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user, check_permissions
from app.schemas.material import MaterialCreate, MaterialUpdate, MaterialOut
from app.crud import material as crud_material
from app.services.storage_service import StorageManager

router = APIRouter()

@router.post("/upload")
async def upload_material_file(
    file: UploadFile = File(...),
    folder: str = Query("assets", description="上传子文件夹路径(如 backgrounds, thumbnails, geojson)"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    通用静态资源上传接口，支持本地存储与 OSS 存储动态切换。
    """
    content = await file.read()
    provider = await StorageManager.get_provider(db)
    try:
        url = await provider.save_file(content, file.filename, folder)
        return {"url": url}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件上传失败: {str(e)}"
        )

@router.delete("/delete-file")
async def delete_material_file(
    file_url: str = Query(..., description="要删除的静态资源文件 URL"),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    物理删除指定的静态资源文件，支持本地和对象存储 (S3/OSS)
    """
    if not file_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="文件 URL 不能为空"
        )
    provider = await StorageManager.get_provider(db)
    try:
        success = await provider.delete_file(file_url)
        if success:
            return {"message": "文件删除成功"}
        else:
            return {"message": "文件不存在或未被删除"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"文件删除失败: {str(e)}"
        )

@router.get("/official", response_model=List[MaterialOut])
async def list_official_materials(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取官方内置素材模版列表（公开接口，免鉴权，方便编辑器免登录使用，或普通用户浏览）
    """
    return await crud_material.get_official_materials(db, category)

@router.get("/my", response_model=List[MaterialOut])
async def list_my_materials(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取当前用户专属的 DIY 素材列表
    """
    return await crud_material.get_user_materials(db, current_user.id, category)

@router.post("/pull/{official_id}", response_model=MaterialOut)
async def pull_official_material(
    official_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    从官方素材库拉取（克隆）一个预设模版到用户专属的 DIY 素材库
    """
    cloned = await crud_material.clone_official_material(
        db, 
        official_id=official_id, 
        user_id=current_user.id, 
        username=current_user.username
    )
    if not cloned:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="官方素材未找到或其不是官方预设"
        )
    return cloned

@router.post("/my", response_model=MaterialOut)
async def create_my_material(
    material_in: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    用户自主创建自定义的专属素材（如配置一个新的 ECharts Option，或绑定已上传的背景图）
    """
    # 强制将所有权绑定为当前用户，且标识为非官方内置
    material_in.creator_id = current_user.id
    material_in.is_official = False
    return await crud_material.create_material(db, material_in, current_user.username)

@router.put("/my/{material_id}", response_model=MaterialOut)
async def update_my_material(
    material_id: int,
    material_in: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    编辑用户自建或已拉取的 DIY 素材
    """
    db_material = await crud_material.get_material_by_id(db, material_id)
    if not db_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="素材不存在"
        )
    # 限制只有素材拥有者可以修改它
    if db_material.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此素材"
        )
    return await crud_material.update_material(db, db_material, material_in, current_user.username)

@router.delete("/my/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_my_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    删除用户专属的 DIY 素材
    """
    db_material = await crud_material.get_material_by_id(db, material_id)
    if not db_material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="素材不存在"
        )
    if db_material.creator_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权操作此素材"
        )
    await crud_material.delete_material(db, material_id)
    return None

# --- 管理员管理官方素材的接口 ---

@router.post("/official", response_model=MaterialOut)
async def create_official_material(
    material_in: MaterialCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:material:manage"))
):
    """
    创建官方内置素材（管理员权限）
    """
    material_in.is_official = True
    material_in.creator_id = None
    return await crud_material.create_material(db, material_in, current_user.username)

@router.put("/official/{material_id}", response_model=MaterialOut)
async def update_official_material(
    material_id: int,
    material_in: MaterialUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:material:manage"))
):
    """
    更新官方内置素材（管理员权限）
    """
    db_material = await crud_material.get_material_by_id(db, material_id)
    if not db_material or not db_material.is_official:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="官方素材未找到"
        )
    return await crud_material.update_material(db, db_material, material_in, current_user.username)

@router.delete("/official/{material_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_official_material(
    material_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:material:manage"))
):
    """
    软删除官方内置素材（管理员权限）
    """
    db_material = await crud_material.get_material_by_id(db, material_id)
    if not db_material or not db_material.is_official:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="官方素材未找到"
        )
    await crud_material.delete_material(db, material_id)
    return None

@router.post("/cleanup-temp")
async def cleanup_unused_files(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(check_permissions("system:material:manage"))
):
    """
    清理存储中未被引用的历史临时文件（管理员权限）
    """
    try:
        from app.services.storage_service import get_all_referenced_urls
        db_urls = await get_all_referenced_urls(db)
        provider = await StorageManager.get_provider(db)
        
        # Cleanup files older than 1 hour (3600 seconds)
        deleted_count = await provider.cleanup_temp_files(db_urls, max_age_seconds=3600)
        return {"deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"临时文件清理失败: {str(e)}"
        )
