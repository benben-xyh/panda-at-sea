"""database.py —— SQLAlchemy 引擎与会话（升级方案 §12）

说明：相对方案中的 async 版本，这里采用同步引擎——本站规模下更简单可靠，
FastAPI 同步路由在线程池中执行不阻塞事件循环。生产切 PostgreSQL 只需改
DATABASE_URL（psycopg2），模型层零改动。
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from .config import settings

connect_args = {"check_same_thread": False} if settings.DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(settings.DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI 依赖：每请求一个会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
