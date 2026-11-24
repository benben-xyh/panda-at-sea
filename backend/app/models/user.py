"""users 表 —— 原云服务认证里的用户「转正」为本地表（升级方案 §13）"""
from datetime import datetime, timezone

from sqlalchemy import BigInteger, DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from ..database import Base

# BigInteger 在 PostgreSQL 是 BIGINT；SQLite 下退化为 INTEGER 以启用自增
PK = BigInteger().with_variant(Integer, "sqlite")


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(PK, primary_key=True, autoincrement=True)
    phone: Mapped[str | None] = mapped_column(String(11), unique=True, index=True)
    nickname: Mapped[str | None] = mapped_column(String(50))
    wx_openid: Mapped[str | None] = mapped_column(String(64), unique=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
