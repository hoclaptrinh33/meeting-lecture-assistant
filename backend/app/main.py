from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes_auth import router as auth_router
from app.api.routes_events import router as events_router
from app.api.routes_export import router as export_router
from app.api.routes_jobs import router as jobs_router
from app.api.routes_live import router as live_router
from app.api.routes_llm import router as llm_router
from app.api.routes_voice import router as voice_router
from app.core.exceptions import AppException, app_exception_handler
from app.schemas.common import HealthResponse

app = FastAPI(
    title="Meeting & Lecture Assistant API",
    version="1.3.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

# CORS Middleware cho môi trường phát triển & web client
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Đăng ký xử lý lỗi chuẩn theo format dự án
app.add_exception_handler(AppException, app_exception_handler)


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "internal_error",
                "message": f"Đã xảy ra lỗi máy chủ nội bộ: {str(exc)}",
            }
        },
    )


# Đăng ký endpoint kiểm tra trạng thái sức khỏe
@app.get("/api/health", response_model=HealthResponse, tags=["health"])
def health_check():
    return HealthResponse(status="ok")


# Đăng ký các router nghiệp vụ
app.include_router(auth_router)
app.include_router(jobs_router)
app.include_router(events_router)
app.include_router(live_router)
app.include_router(voice_router)
app.include_router(llm_router)
app.include_router(export_router)
