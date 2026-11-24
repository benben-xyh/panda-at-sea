"""config.py —— 环境配置（读环境变量，全部有默认值，开箱即用）

对应升级方案 §12：
  DATABASE_URL  开发默认 SQLite，生产切 PostgreSQL（postgres+psycopg2://...）
  JWT_SECRET    生产必须改！生成方式：python -c "import secrets;print(secrets.token_urlsafe(48))"
  REDIS_URL     为空时 OTP 降级为进程内存存储（开发够用，生产务必配 Redis）
  SMS_MODE      console=验证码打到日志（开发）；tencent=接腾讯云短信（生产）
"""
import os
import secrets


class Settings:
    # ---- 应用 ----
    APP_NAME: str = "熊猫海上 API"
    VERSION: str = "2.0.0"
    # CORS：生产改为前端域名，逗号分隔
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", "http://localhost:5173,http://localhost:4173"
    ).split(",")

    # ---- 数据库 ----
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./blog.db")

    # ---- JWT ----
    JWT_SECRET: str = os.getenv("JWT_SECRET", "dev-only-" + secrets.token_urlsafe(24))
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_MINUTES: int = int(os.getenv("ACCESS_TOKEN_MINUTES", "30"))
    REFRESH_TOKEN_DAYS: int = int(os.getenv("REFRESH_TOKEN_DAYS", "7"))

    # ---- OTP ----
    OTP_TTL_SECONDS: int = 300          # 验证码有效期 5 分钟
    OTP_RESEND_SECONDS: int = 60        # 服务端频控：同号 60s 内只发一次
    REDIS_URL: str = os.getenv("REDIS_URL", "")

    # ---- 短信 ----
    SMS_MODE: str = os.getenv("SMS_MODE", "console")  # console | tencent
    SMS_SECRET_ID: str = os.getenv("SMS_SECRET_ID", "")
    SMS_SECRET_KEY: str = os.getenv("SMS_SECRET_KEY", "")
    SMS_SDK_APP_ID: str = os.getenv("SMS_SDK_APP_ID", "")
    SMS_TEMPLATE_ID: str = os.getenv("SMS_TEMPLATE_ID", "")
    SMS_SIGN_NAME: str = os.getenv("SMS_SIGN_NAME", "")

    # ---- 刷新 cookie ----
    REFRESH_COOKIE: str = "refresh_token"


settings = Settings()
