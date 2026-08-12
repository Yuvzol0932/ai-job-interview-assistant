"""FastAPI 应用入口：注册中间件与路由。"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from api.routers import interview, reports, resume
from services.job_catalog import job_labels

app = FastAPI(title="AI 求职面试助手 API", version="0.3")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(resume.router)
app.include_router(interview.router)
app.include_router(reports.router)


@app.exception_handler(Exception)
async def unhandled_exception(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(status_code=500, content={"error": "服务器内部错误，请稍后重试。"})


@app.get("/api/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/api/jobs")
def jobs() -> dict:
    return {"labels": job_labels()}
