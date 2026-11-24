"""schemas —— Pydantic v2 请求/响应模型（升级方案 §12）

安全约定：PostCreate/PostUpdate **不包含 owner_id 字段**——
作者身份永远由服务层从 JWT 注入，客户端无法伪造（等价原 WITH CHECK）。
"""
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


# ---------- Auth ----------

class OtpRequest(BaseModel):
    phone: str = Field(pattern=r"^1\d{10}$", description="11 位手机号")


class OtpVerify(BaseModel):
    phone: str = Field(pattern=r"^1\d{10}$")
    code: str = Field(min_length=4, max_length=8)


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    phone: str | None
    nickname: str | None


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut
    is_new_user: bool = False


# ---------- Posts ----------

class PostCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)
    summary: str | None = Field(default=None, max_length=120)
    content: str | None = None
    status: str = Field(default="published", pattern=r"^(published|draft)$")


class PostUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=100)
    summary: str | None = Field(default=None, max_length=120)
    content: str | None = None


class PostOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    owner_id: int
    owner_name: str | None
    title: str
    summary: str | None
    content: str | None
    status: str
    created_at: datetime
    updated_at: datetime


# ---------- Comments ----------

class CommentCreate(BaseModel):
    content: str = Field(min_length=1, max_length=500)


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    post_id: int
    owner_id: int
    owner_name: str | None
    content: str
    created_at: datetime
