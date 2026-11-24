"""test_api.py —— 对测原 7 条 RLS 语义（升级方案 §17 风险表「权限漏写」的对策）

用 SQLite 内存库 + httpx 直调 FastAPI，覆盖：
  1 posts_read_published_or_own   匿名只见 published
  2 posts_insert_own              匿名发文 401；登录发文 201 且 owner 为本人
  3 posts_update_own              非作者 PATCH 403；作者成功
  4 posts_delete_own              非作者 DELETE 403；作者 204
  5 comments_read_all             公开可读
  6 comments_insert_own           未登录 401；登录 201
  7 comments_delete_own           非作者 403；作者 204
"""
import os
import sys

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["JWT_SECRET"] = "test-secret"
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest
from fastapi.testclient import TestClient

from app.database import SessionLocal, engine, Base
from app.main import app
from app.models import Post, User


@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    with SessionLocal() as db:
        db.add(User(id=1, phone="13800000001", nickname="作者甲"))
        db.add(User(id=2, phone="13800000002", nickname="作者乙"))
        db.add(Post(id=1, owner_id=1, owner_name="作者甲", title="甲的已发布", status="published", content="hello"))
        db.add(Post(id=2, owner_id=1, owner_name="作者甲", title="甲的草稿", status="draft"))
        db.commit()
    yield
    os.remove("./test.db")


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as c:
        yield c


def login(client: TestClient, phone: str) -> dict:
    """console 短信模式：验证码在日志里，这里直接从 otp_store 取（测试捷径）"""
    from app.core.otp_store import otp_store, MemoryStore
    code = "123456"
    otp_store._codes[phone] = (code, 9e99) if isinstance(otp_store, MemoryStore) else None
    r = client.post("/api/auth/otp/verify", json={"phone": phone, "code": code})
    assert r.status_code == 200, r.text
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_1_read_published_or_own(client):
    # 匿名：只见 published
    r = client.get("/api/posts")
    assert r.status_code == 200
    titles = [p["title"] for p in r.json()]
    assert "甲的已发布" in titles and "甲的草稿" not in titles
    # 匿名读草稿详情 → 404（不暴露存在性）
    assert client.get("/api/posts/2").status_code == 404
    # 作者读自己的草稿 → 200
    h = login(client, "13800000001")
    assert client.get("/api/posts/2", headers=h).status_code == 200


def test_2_insert_own(client):
    # 匿名发文 → 401
    assert client.post("/api/posts", json={"title": "游客的文章"}).status_code == 401
    # 登录发文 → 201，owner 自动为本人
    h2 = login(client, "13800000002")
    r = client.post("/api/posts", json={"title": "乙的新文章"}, headers=h2)
    assert r.status_code == 201
    body = r.json()
    assert body["owner_id"] == 2 and body["owner_name"] == "作者乙"


def test_3_update_own(client):
    h2 = login(client, "13800000002")
    # 非作者改甲的文章 → 403
    assert client.patch("/api/posts/1", json={"title": "篡改"}, headers=h2).status_code == 403
    # 作者改自己的 → 200
    h1 = login(client, "13800000001")
    r = client.patch("/api/posts/1", json={"title": "甲改好了"}, headers=h1)
    assert r.status_code == 200 and r.json()["title"] == "甲改好了"


def test_4_delete_own(client):
    h2 = login(client, "13800000002")
    h1 = login(client, "13800000001")
    # 先建一篇专用于删除测试的文章（不影响后续评论测试用的文章 1）
    r = client.post("/api/posts", json={"title": "待撕的文章"}, headers=h1)
    del_id = r.json()["id"]
    # 非作者删 → 403；作者删 → 204
    assert client.delete(f"/api/posts/{del_id}", headers=h2).status_code == 403
    assert client.delete(f"/api/posts/{del_id}", headers=h1).status_code == 204


def test_5_comments_read_all(client):
    h1 = login(client, "13800000001")
    client.post("/api/posts/1/comments", json={"content": "第一条便签"}, headers=h1)
    # 匿名可读评论
    r = client.get("/api/posts/1/comments")
    assert r.status_code == 200 and len(r.json()) == 1


def test_6_comments_insert_own(client):
    # 未登录 → 401；登录 → 201 且 owner 为本人
    assert client.post("/api/posts/1/comments", json={"content": "x"}).status_code == 401
    h2 = login(client, "13800000002")
    r = client.post("/api/posts/1/comments", json={"content": "乙的便签"}, headers=h2)
    assert r.status_code == 201 and r.json()["owner_id"] == 2


def test_7_comments_delete_own(client):
    h2 = login(client, "13800000002")
    h1 = login(client, "13800000001")
    # 甲划不掉乙的便签 → 403
    assert client.delete("/api/comments/2", headers=h1).status_code == 403
    # 乙划自己的 → 204
    assert client.delete("/api/comments/2", headers=h2).status_code == 204
