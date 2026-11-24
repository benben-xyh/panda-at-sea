FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt "sqlalchemy<2.1" "psycopg[binary]"
COPY app ./app
COPY seed_data.json ./
EXPOSE 8000
# 生产先跑迁移与种子（幂等），再启动
CMD ["sh", "-c", "python scripts/seed_db.py || true; uvicorn app.main:app --host 0.0.0.0 --port 8000"]
