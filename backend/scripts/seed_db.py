"""seed_db.py —— 云数据库 → 自建数据库 一次性导入（升级方案 §13/§5.2）

映射逻辑（对应方案 map_owner 步骤）：
  云端 owner_id（auth.uid 字符串，如 "system"）→ 按 owner_name 去重合并成 users 行 → 新自增 ID
  文章/评论 owner_id 全部改写为新 users.id

用法：
  python scripts/seed_db.py            # 读 ../seed_data.json 导入当前 DATABASE_URL
"""
import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.database import Base, SessionLocal, engine  # noqa: E402
from app.models import Comment, Post, User  # noqa: E402
from app.models.user import utcnow  # noqa: E402
from datetime import datetime  # noqa: E402


def parse_ts(s: str):
    return datetime.fromisoformat(s) if s else utcnow()


def main() -> None:
    seed_path = os.path.join(os.path.dirname(__file__), "..", "seed_data.json")
    data = json.load(open(seed_path, encoding="utf-8"))

    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)

    db = SessionLocal()
    try:
        name_to_user: dict[str, User] = {}
        post_id_map: dict[int, int] = {}   # 云端 post_id → 新 post_id
        n_posts = n_comments = 0

        for group in data:
            uname = group.get("owner_name") or "匿名船员"
            user = name_to_user.get(uname)
            if user is None:
                user = User(nickname=uname)   # 云端无手机号，导入用户仅作归属记录
                db.add(user)
                db.flush()
                name_to_user[uname] = user

            for p in group.get("posts", []):
                post = Post(
                    owner_id=user.id,
                    owner_name=uname,
                    title=p["title"],
                    summary=p.get("summary"),
                    content=p.get("content"),
                    status=p.get("status", "published"),
                    created_at=parse_ts(p.get("created_at")),
                    updated_at=parse_ts(p.get("updated_at")),
                )
                db.add(post)
                db.flush()
                post_id_map[p["cloud_post_id"]] = post.id
                n_posts += 1

            for c in group.get("comments", []):
                db.add(Comment(
                    post_id=post_id_map[c["post_id"]],   # 重映射云端 ID
                    owner_id=user.id,
                    owner_name=uname,
                    content=c["content"],
                    created_at=parse_ts(c.get("created_at")),
                ))
                n_comments += 1

        db.commit()
        print(f"导入完成：users={len(name_to_user)} posts={n_posts} comments={n_comments}")
    finally:
        db.close()


if __name__ == "__main__":
    main()
