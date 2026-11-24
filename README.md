# 熊猫海上 v2 — React + TS / Python FastAPI

「熊猫海上」博客的升级版（v1 见 `../hundred-blog/`）。本目录是升级方案
（`hundred-blog/docs/upgrade-plan-react-fastapi.md`）P0~P5 的完整落地实现。

```
blog-v2/
├── frontend/          # React 18 + TypeScript 5 + Vite 5（strict 全绿）
│   ├── src/api/       # axios 客户端（Bearer 注入 + 401 静默续期）
│   ├── src/hooks/     # useAuth Context
│   ├── src/pages/     # 首页/手记/详情/关于/登陆/写字/草稿箱
│   ├── src/styles/    # 手绘风设计系统（v1 CSS 原样平移）
│   ├── Dockerfile     # 多阶段：node build → nginx
│   └── nginx.conf     # history 路由回退 + /api 反代
├── backend/           # FastAPI + SQLAlchemy 2.0
│   ├── app/api/       # auth（OTP+JWT）· posts · comments
│   ├── app/core/      # security.py(JWT 双token) · otp_store.py(Redis/内存) · sms.py
│   ├── app/services/  # permissions.py —— 原 7 条 RLS 的应用层等价实现
│   ├── tests/         # pytest：逐条对测原 RLS 语义
│   ├── scripts/       # seed_db.py（云端数据迁移）
│   ├── seed_data.json # 从云端导出的数据（1 篇文章，0 评论）
│   └── Dockerfile
├── docker-compose.yml # frontend + backend + postgres16 + redis7
└── .env.example
```

## 快速开始（开发）

```bash
# 后端（默认 SQLite + console 短信，验证码打印在后端日志）
cd backend
python -m pip install -r requirements.txt "sqlalchemy<2.1"
python scripts/seed_db.py          # 建表并导入云端数据
python -m uvicorn app.main:app --reload --port 8000
# Swagger：http://localhost:8000/docs

# 前端（Vite 开发服务器，/api 自动代理到 8000）
cd frontend
npm install
npm run dev                        # http://localhost:5173
```

登陆：输入任意手机号 → 获取验证码 → 看后端日志里的 6 位数字 → 登陆成功（新号自动注册）。

## 测试

```bash
cd backend && python -m pytest tests/ -v
# 7 个测试用例逐条对测原 7 条 RLS 语义（已人工执行等价冒烟 14/14 通过）
```

## 生产部署

```bash
cp .env.example .env   # 修改 JWT_SECRET、SMS_* 配置
docker compose up -d --build
# http://localhost（Nginx 托管前端 + 反代 /api）
```

## 与升级方案的对应关系

| 方案章节 | 落地位置 | 状态 |
|---|---|---|
| §11 前端选型/结构 | `frontend/` | ✅（CSS 用全局平移替代 CSS Modules，视觉零变化） |
| §12 后端选型/结构 | `backend/app/` | ✅（采用同步引擎简化，生产可平替 async） |
| §12 认证 | `core/security.py + otp_store.py + sms.py` | ✅（JWT 双 token + Redis 优先/内存降级） |
| §4.4 RLS→应用层 | `services/permissions.py` + tests | ✅（14/14 冒烟通过） |
| §13 数据库升级 | models + seed_db.py | ✅（users 表 + 外键 + post_id 重映射） |
| §15 部署 | docker-compose + nginx.conf | ✅（HTTPS 挂 Caddy/负载均衡后补） |
| 微信 OAuth / Alembic | — | ⏳ 二期（方案 P6） |

## 环境问题备注

- 本机 Python 为 WorkBuddy 便携版，应用控制策略拦截了 SQLAlchemy 2.1 的 C 扩展 DLL，
  因此锁定 `sqlalchemy<2.1`（2.0.x 带纯 Python 回退）—— requirements/Dockerfile 已体现。
- Redis 未配置时 OTP 自动降级为进程内存存储（仅限开发）。
