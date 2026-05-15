from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate, UserListResponse, AdminCreateUser
from app.utils.auth import (
    get_password_hash,
    verify_password,
    create_access_token,
    get_current_user,
)
from app.utils.logger import logger

def require_admin(current_user: User = Depends(get_current_user)) -> User:
    """要求管理员权限"""
    if current_user.role != 'admin':
        raise HTTPException(status_code=403, detail="需要管理员权限")
    return current_user

router = APIRouter(prefix="/api/auth", tags=["认证"])


@router.post("/register", response_model=Token, summary="用户注册")
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Check existing username
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    # Check email uniqueness only when provided
    if user_data.email and user_data.email.strip():
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        username=user_data.username,
        email=user_data.email or None,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name or "",
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": str(user.id)})
    logger.info(f"新用户注册: {user.username}")
    return Token(access_token=token, user=UserResponse.from_user(user))


@router.post("/login", response_model=Token, summary="用户登录")
async def login(login_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == login_data.username).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="用户已被禁用")

    token = create_access_token({"sub": str(user.id)})
    logger.info(f"用户登录: {user.username}")
    return Token(access_token=token, user=UserResponse.from_user(user))


@router.get("/me", response_model=UserResponse, summary="获取当前用户信息")
async def get_me(current_user: User = Depends(get_current_user)):
    return UserResponse.from_user(current_user)


@router.put("/me", response_model=UserResponse, summary="更新当前用户信息")
async def update_me(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    update_dict = update_data.model_dump(exclude_unset=True)
    # 如果包含密码，需要哈希处理
    if "password" in update_dict:
        password = update_dict.pop("password")
        if password:
            current_user.hashed_password = get_password_hash(password)
    for field, value in update_dict.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return UserResponse.from_user(current_user)


# ==================== 用户管理 (管理员专用) ====================

@router.get("/users", response_model=UserListResponse, summary="获取用户列表")
async def list_users(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    keyword: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """获取所有用户列表（仅管理员）"""
    query = db.query(User)
    if keyword:
        query = query.filter(
            User.username.contains(keyword) | User.email.contains(keyword) | User.full_name.contains(keyword)
        )
    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * page_size).limit(page_size).all()

    return UserListResponse(
        items=[UserResponse.from_user(u) for u in users],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/users", response_model=UserResponse, summary="创建用户")
async def create_user(
    user_data: AdminCreateUser,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """创建新用户（仅管理员）"""
    if db.query(User).filter(User.username == user_data.username).first():
        raise HTTPException(status_code=400, detail="用户名已存在")
    if user_data.email and user_data.email.strip():
        if db.query(User).filter(User.email == user_data.email).first():
            raise HTTPException(status_code=400, detail="邮箱已被注册")

    user = User(
        username=user_data.username,
        email=user_data.email or None,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name or "",
        role=user_data.role or "member",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    logger.info(f"管理员 {current_user.username} 创建用户: {user.username}")
    return UserResponse.from_user(user)


@router.put("/users/{user_id}", response_model=UserResponse, summary="更新用户")
async def update_user(
    user_id: int,
    update_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """更新用户信息（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 不允许修改自己的角色
    if user_id == current_user.id and update_data.role:
        raise HTTPException(status_code=400, detail="不能修改自己的角色")

    update_dict = update_data.model_dump(exclude_unset=True)
    # 如果包含密码，需要哈希处理
    if "password" in update_dict:
        password = update_dict.pop("password")
        if password:
            user.hashed_password = get_password_hash(password)
    for field, value in update_dict.items():
        setattr(user, field, value)
    db.commit()
    db.refresh(user)
    logger.info(f"管理员 {current_user.username} 更新用户: {user.username}")
    return UserResponse.from_user(user)


@router.delete("/users/{user_id}", summary="删除用户")
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_admin),
):
    """删除用户（仅管理员）"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己")

    db.delete(user)
    db.commit()
    logger.info(f"管理员 {current_user.username} 删除用户: {user.username}")
    return {"message": "删除成功"}
