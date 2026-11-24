"""otp_store.py —— 验证码存储：Redis 优先，无 Redis 时降级为进程内存

原方案前端 60s 倒计时只是体验层；这里把频控做在服务端（升级方案 §12）：
  set(phone, code)   写入，TTL 300s；同号 60s 内重复请求抛 429
  verify(phone, code) 校验并消费（一次性）
"""
import time
from typing import Protocol

from fastapi import HTTPException, status

from ..config import settings


class OtpStore(Protocol):
    def set(self, phone: str, code: str) -> None: ...
    def verify(self, phone: str, code: str) -> None: ...


class RedisStore:
    def __init__(self, url: str):
        import redis  # 延迟导入：未装 redis 或无服务时走内存降级
        self._r = redis.from_url(url, decode_responses=True)
        self._r.ping()  # 连不上直接抛错，让启动期暴露问题

    def set(self, phone: str, code: str) -> None:
        if self._r.exists(f"otp:lock:{phone}"):
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "发送太频繁，请稍后再试")
        self._r.setex(f"otp:code:{phone}", settings.OTP_TTL_SECONDS, code)
        self._r.setex(f"otp:lock:{phone}", settings.OTP_RESEND_SECONDS, "1")

    def verify(self, phone: str, code: str) -> None:
        key = f"otp:code:{phone}"
        saved = self._r.get(key)
        if not saved or saved != code:
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "验证码错误或已过期")
        self._r.delete(key)


class MemoryStore:
    """开发降级实现：dict + 过期时间戳（单进程内有效）"""

    def __init__(self):
        self._codes: dict[str, tuple[str, float]] = {}
        self._locks: dict[str, float] = {}

    def set(self, phone: str, code: str) -> None:
        now = time.time()
        if self._locks.get(phone, 0) > now:
            raise HTTPException(status.HTTP_429_TOO_MANY_REQUESTS, "发送太频繁，请稍后再试")
        self._codes[phone] = (code, now + settings.OTP_TTL_SECONDS)
        self._locks[phone] = now + settings.OTP_RESEND_SECONDS

    def verify(self, phone: str, code: str) -> None:
        item = self._codes.get(phone)
        if not item or item[0] != code or item[1] < time.time():
            raise HTTPException(status.HTTP_400_BAD_REQUEST, "验证码错误或已过期")
        del self._codes[phone]


def make_otp_store() -> OtpStore:
    if settings.REDIS_URL:
        try:
            return RedisStore(settings.REDIS_URL)
        except Exception as exc:  # Redis 不可用 → 降级并提示
            print(f"[otp] Redis 不可用（{exc}），降级为内存存储（仅限开发环境）")
    return MemoryStore()


otp_store: OtpStore = make_otp_store()
