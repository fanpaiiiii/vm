"""
文件上传 API
支持图片上传，保存到 backend/uploads/ 目录
"""
import os
import uuid
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.staticfiles import StaticFiles
from app.models.user import User
from app.utils.auth import get_current_user
from app.utils.logger import logger

router = APIRouter(prefix="/api/upload", tags=["文件上传"])

# 上传目录
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

# 允许的文件类型
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/image", summary="上传图片")
async def upload_image(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """上传图片文件，返回访问URL"""
    
    # 验证文件类型
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=400,
            detail=f"不支持的文件类型: {file.content_type}。允许: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
    
    # 读取文件内容
    content = await file.read()
    
    # 验证文件大小
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"文件太大: {len(content) / 1024 / 1024:.1f}MB。最大允许: {MAX_FILE_SIZE / 1024 / 1024}MB"
        )
    
    # Verify file content matches declared type
    MAGIC_BYTES = {
        'image/jpeg': [b'\xff\xd8\xff'],
        'image/png': [b'\x89PNG'],
        'image/gif': [b'GIF87a', b'GIF89a'],
        'image/webp': [b'RIFF'],
    }
    expected_magic = MAGIC_BYTES.get(file.content_type, [])
    if expected_magic and not any(content.startswith(m) for m in expected_magic):
        raise HTTPException(status_code=400, detail='文件内容与声明的类型不匹配')
    
    # 生成唯一文件名
    ext = os.path.splitext(file.filename)[1] if file.filename else ".jpg"
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    
    # 保存文件
    with open(filepath, "wb") as f:
        f.write(content)
    
    # 返回访问URL
    url = f"/uploads/{filename}"
    logger.info(f"图片上传成功: {filename} (用户: {current_user.username})")
    
    return {
        "url": url,
        "filename": filename,
        "size": len(content),
        "content_type": file.content_type,
    }


@router.get("/images", summary="获取已上传图片列表")
async def list_images(
    current_user: User = Depends(get_current_user),
):
    """获取已上传的图片列表"""
    if not os.path.exists(UPLOAD_DIR):
        return {"images": []}
    
    images = []
    for filename in os.listdir(UPLOAD_DIR):
        filepath = os.path.join(UPLOAD_DIR, filename)
        if os.path.isfile(filepath):
            stat = os.stat(filepath)
            images.append({
                "filename": filename,
                "url": f"/uploads/{filename}",
                "size": stat.st_size,
                "created_at": stat.st_ctime,
            })
    
    # 按创建时间倒序
    images.sort(key=lambda x: x["created_at"], reverse=True)
    return {"images": images}
