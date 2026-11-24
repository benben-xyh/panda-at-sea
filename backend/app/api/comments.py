"""api/comments.py —— 边角便签端点（升级方案 §14）"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..core.security import get_current_user, get_optional_user
from ..database import get_db
from ..models import Comment, Post, User
from ..schemas import CommentCreate, CommentOut
from ..services.permissions import ensure_can_edit_comment, ensure_post_visible

router = APIRouter(tags=["comments"])


@router.get("/posts/{post_id}/comments", response_model=list[CommentOut])
def list_comments(
    post_id: int,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> list[CommentOut]:
    """等价 comments_read_all：公开可读（但文章本身要先可见）"""
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "这一页被撕掉了（文章不存在）")
    ensure_post_visible(post, user)
    rows = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(Comment.created_at.asc())
        .all()
    )
    return [CommentOut.model_validate(c) for c in rows]


@router.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=201)
def create_comment(
    post_id: int,
    body: CommentCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CommentOut:
    """贴便签：等价 comments_insert_own（owner 由服务层注入）"""
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "这一页被撕掉了（文章不存在）")
    ensure_post_visible(post, user)
    comment = Comment(
        post_id=post_id,
        owner_id=user.id,                      # ← 服务层注入
        owner_name=user.nickname,
        content=body.content,
    )
    db.add(comment)
    db.commit()
    return CommentOut.model_validate(comment)


@router.delete("/comments/{comment_id}", status_code=204)
def delete_comment(
    comment_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """划掉：等价 comments_delete_own"""
    comment = db.get(Comment, comment_id)
    if comment is None:
        raise HTTPException(404, "便签不存在")
    ensure_can_edit_comment(comment, user)
    db.delete(comment)
    db.commit()
