from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: Optional[str] = ""
    password: str = Field(min_length=6)
    full_name: Optional[str] = ""


class UserLogin(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
    avatar: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class AdminCreateUser(BaseModel):
    username: str = Field(min_length=2, max_length=50)
    email: Optional[str] = ""
    password: str = Field(min_length=6)
    full_name: Optional[str] = ""
    role: Optional[str] = "user"


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str
    is_active: bool
    avatar: str
    created_at: Optional[datetime] = None
    # 前端兼容字段
    userId: Optional[int] = None
    userName: Optional[str] = None
    roles: Optional[List[str]] = None
    buttons: Optional[List[str]] = None

    class Config:
        from_attributes = True

    @classmethod
    def from_user(cls, user):
        """从用户模型创建响应，自动填充前端兼容字段"""
        return cls(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            is_active=user.is_active,
            avatar=user.avatar or "",
            created_at=user.created_at,
            userId=user.id,
            userName=user.username,
            roles=[user.role] if user.role else ["user"],
            buttons=[]
        )


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    user_id: Optional[int] = None


class UserListResponse(BaseModel):
    items: List[UserResponse]
    total: int
    page: int
    page_size: int
