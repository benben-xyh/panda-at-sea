"""security.py —— JWT 双 token 签发/校验 + FastAPI 依赖（升级方案 §12、§4.3/4.4）

替代原云服务的会话管理：
  - access token：30 分钟，前端内存持有，Authorization: Bearer
  - refresh token：7 天，httpOnly cookie（JS 读不到，XSS 偷不走）
  - get_current_user：替代「authenticated 角色」判断
  - get_optional_user：替代「anon 也能读」的场景
"""
from datetime import datetime, timedelta, timezone

from fastapi import Cookie, Depends, HTTPException, Request, status
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from ..config import settings
from ..database import get_db
from ..models import User

SUB_KEY = "sub"


def _create_token(user_id: int, expires_delta: timedelta) -> str:
    payload = {
        SUB_KEY: str(user_id),
        "exp": datetime.now(timezone.utc) + expires_delta,
        "iat": datetime.now(timezone.utc),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def create_access_token(user_id: int) -> str:
    return _create_token(user_id, timedelta(minutes=settings.ACCESS_TOKEN_MINUTES))


def create_refresh_token(user_id: int) -> str:
    return _create_token(user_id, timedelta(days=settings.REFRESH_TOKEN_DAYS))


def decode_token(token: str) -> int:
    """解析并校验 token，返回 user_id；非法/过期抛 401"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "凭证无效或已过期，请重新登陆")
    user_id = payload.get(SUB_KEY)
    if user_id is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "凭证无效")
    return int(user_id)


def _extract_bearer(request: Request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        return auth[7:]
    return None


def get_current_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User:
    """强依赖：未登陆一律 401（替代 RLS 的 authenticated 判定）"""
    token = _extract_bearer(request)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "请先登船签到")
    user = db.get(User, decode_token(token))
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在")
    return user


def get_optional_user(
    request: Request,
    db: Session = Depends(get_db),
) -> User | None:
    """弱依赖：匿名返回 None（替代 RLS 的 anon 角色）"""
    token = _extract_bearer(request)
    if not token:
        return None
    try:
        user = db.get(User, decode_token(token))
    except HTTPException:
        return None
    return user


def refresh_token_from_cookie(refresh_token: str | None = Cookie(default=None)) -> int:
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "缺少 refresh token")
    return decode_token(refresh_token)
