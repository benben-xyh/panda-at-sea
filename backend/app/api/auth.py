"""api/auth.py —— 认证端点：OTP 两步 + JWT 双 token（升级方案 §12）

保持原体验：新手机号验证后自动注册（免密码）。
"""
import secrets

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from ..config import settings
from ..core.otp_store import otp_store
from ..core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_current_user,
    refresh_token_from_cookie,
)
from ..core.sms import send_otp_sms
from ..database import get_db
from ..models import User
from ..schemas import OtpRequest, OtpVerify, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

REFRESH_COOKIE_KW = {
    "httponly": True,
    "secure": True,          # 生产 HTTPS；本地 http 调试时可临时改 False
    "samesite": "lax",
    "path": "/api/auth",
    "max_age": settings.REFRESH_TOKEN_DAYS * 86400,
}


@router.post("/otp/request")
def request_otp(body: OtpRequest) -> dict:
    """第一步：请求验证码（服务端 60s 频控，不再依赖前端倒计时）"""
    code = f"{secrets.randbelow(1000000):06d}"
    otp_store.set(body.phone, code)          # 频控在这里，重复请求抛 429
    note = send_otp_sms(body.phone, code)
    return {"code": 0, "msg": note}


@router.post("/otp/verify", response_model=TokenResponse)
def verify_otp(body: OtpVerify, response: Response, db: Session = Depends(get_db)) -> TokenResponse:
    """第二步：验证 + 自动注册 + 签发双 token"""
    otp_store.verify(body.phone, body.code)

    user = db.query(User).filter(User.phone == body.phone).first()
    is_new = user is None
    if is_new:
        user = User(phone=body.phone, nickname=f"船员{body.phone[-4:]}")
        db.add(user)
        db.commit()

    response.set_cookie(settings.REFRESH_COOKIE, create_refresh_token(user.id), **REFRESH_COOKIE_KW)
    return TokenResponse(
        access_token=create_access_token(user.id),
        user=UserOut.model_validate(user),
        is_new_user=is_new,
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(response: Response, user_id: int = Depends(refresh_token_from_cookie),
            db: Session = Depends(get_db)) -> TokenResponse:
    """用 refresh cookie 换新 access token（axios 拦截器静默调用）"""
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "用户不存在")
    response.set_cookie(settings.REFRESH_COOKIE, create_refresh_token(user.id), **REFRESH_COOKIE_KW)
    return TokenResponse(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/logout")
def logout(response: Response) -> dict:
    """下船：清 refresh cookie（无状态 JWT 即时失效靠前端丢弃 access）"""
    response.delete_cookie(settings.REFRESH_COOKIE, path="/api/auth")
    return {"code": 0, "msg": "已下船"}


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(user)
