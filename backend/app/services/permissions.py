"""permissions.py —— 原 7 条 RLS 策略的应用层等价实现（升级方案 §12/§4.4）

这是本项目唯一的安全边界转移点：数据库层不再有 RLS，
全部「谁能动什么」的判断集中在本模块，供 pytest 逐条对测。
"""
from fastapi import HTTPException, status

from ..models import Comment, Post, User


def ensure_can_edit_post(post: Post, user: User) -> None:
    """等价 posts_update_own / posts_delete_own: USING (owner_id = auth.uid())"""
    if post.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "这页不是你写的")


def ensure_can_edit_comment(comment: Comment, user: User) -> None:
    """等价 comments_delete_own"""
    if comment.owner_id != user.id:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "这张便签不是你贴的")


def ensure_post_visible(post: Post, user: User | None) -> None:
    """等价 posts_read_published_or_own：草稿仅作者可见，否则按 404 处理（不暴露存在性）"""
    if not post.visible_to(user.id if user else None):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "这一页被撕掉了（文章不存在）")


def post_read_filter(user: User | None) -> dict:
    """列表查询条件：匿名仅 published；登录者 published 或自己的"""
    if user is None:
        return {"status": "published"}
    return {"_or": [{"status": "published"}, {"owner_id": user.id}]}
