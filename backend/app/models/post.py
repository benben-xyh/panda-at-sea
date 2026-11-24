"""posts 表 —— owner_id 从「TEXT 存 auth.uid()」升级为 users 外键（升级方案 §13）

权限语义与原 RLS 对齐：
  - 匿名只见 published；作者额外可见自己的草稿（查询层实现，见 api/posts.py）
  - 改/删仅限作者本人（services/permissions.ensure_can_edit）
"""
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..database import Base
from .user import PK, User, utcnow


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(PK, primary_key=True, autoincrement=True)
    owner_id: Mapped[int] = mapped_column(PK, ForeignKey("users.id"), index=True)
    owner_name: Mapped[str | None] = mapped_column(String(50))   # 昵称冗余，列表页免联查
    title: Mapped[str] = mapped_column(String(100))
    summary: Mapped[str | None] = mapped_column(String(120))     # 关键词句
    content: Mapped[str | None] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(16), default="published")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )

    owner: Mapped[User] = relationship(lazy="joined")

    def visible_to(self, user_id: int | None) -> bool:
        """等价原 RLS: status='published' OR owner_id = auth.uid()"""
        return self.status == "published" or self.owner_id == user_id
