"""api/posts.py —— 手记端点（升级方案 §14）

读：等价 posts_read_published_or_own（匿名仅 published）
写：等价 posts_insert_own / update_own / delete_own（服务层注入 owner_id + 权限校验）
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import or_
from sqlalchemy.orm import Session

from ..core.security import get_current_user, get_optional_user
from ..database import get_db
from ..models import Post, User
from ..schemas import PostCreate, PostOut, PostUpdate
from ..services.permissions import ensure_can_edit_post, ensure_post_visible

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=list[PostOut])
def list_posts(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    q: str | None = None,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> list[PostOut]:
    """手记索引：匿名仅见已发布；q 匹配标题/关键词句"""
    query = db.query(Post)
    if user is None:
        query = query.filter(Post.status == "published")
    else:
        query = query.filter(or_(Post.status == "published", Post.owner_id == user.id))
    if q:
        kw = f"%{q.strip()}%"
        query = query.filter(or_(Post.title.like(kw), Post.summary.like(kw)))
    rows = (
        query.order_by(Post.created_at.desc())
        .offset((page - 1) * size)
        .limit(size)
        .all()
    )
    return [PostOut.model_validate(p) for p in rows]


@router.get("/{post_id}", response_model=PostOut)
def get_post(
    post_id: int,
    user: User | None = Depends(get_optional_user),
    db: Session = Depends(get_db),
) -> PostOut:
    """详情：草稿仅作者可见（否则 404，不暴露存在性）"""
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "这一页被撕掉了（文章不存在）")
    ensure_post_visible(post, user)
    return PostOut.model_validate(post)


@router.post("", response_model=PostOut, status_code=201)
def create_post(
    body: PostCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostOut:
    """发表：owner_id 由服务层注入（等价 WITH CHECK，客户端不可指定）"""
    post = Post(
        owner_id=user.id,                      # ← 服务层注入，等价 DEFAULT auth.uid()
        owner_name=user.nickname,
        title=body.title,
        summary=body.summary,
        content=body.content,
        status=body.status,
    )
    db.add(post)
    db.commit()
    return PostOut.model_validate(post)


@router.patch("/{post_id}", response_model=PostOut)
def update_post(
    post_id: int,
    body: PostUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> PostOut:
    """编辑：等价 posts_update_own USING (owner_id = auth.uid())"""
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "这一页被撕掉了（文章不存在）")
    ensure_can_edit_post(post, user)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(post, field, value)
    db.commit()
    return PostOut.model_validate(post)


@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    """撕掉这页：等价 posts_delete_own"""
    post = db.get(Post, post_id)
    if post is None:
        raise HTTPException(404, "这一页被撕掉了（文章不存在）")
    ensure_can_edit_post(post, user)
    db.delete(post)
    db.commit()
