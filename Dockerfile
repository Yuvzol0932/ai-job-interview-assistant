# Hugging Face Spaces 部署：镜像内构建 React 前端并运行 FastAPI（同端口托管页面与 API）
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates && rm -rf /var/lib/apt/lists/*
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

WORKDIR /app/web
RUN npm install && npm run build

WORKDIR /app

# 默认演示模式；真实模型请在 HF Space 的 Secrets 里配置 LLM_API_KEY 并设 LLM_MODE=real
ENV LLM_MODE=mock
EXPOSE 7860

CMD ["uvicorn", "api.app:app", "--host", "0.0.0.0", "--port", "7860"]
