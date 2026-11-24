"""comments 表（边角便签）—— post 级联删除，owner 外键化（升级方案 §13）"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .user import PK, User, utcnow


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[int] = mapped_column(PK, primary_key=True, autoincrement=True)
    post_id: Mapped[int] = mapped_column(
        PK, ForeignKey("posts.id", ondelete="CASCADE"), index=True
    )
    owner_id: Mapped[int] = mapped_column(PK, ForeignKey("users.id"), index=True)
    owner_name: Mapped[str | None] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    owner: Mapped[User] = relationship(lazy="joined")
