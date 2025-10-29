"""FastAPI主应用入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import uvicorn
import logging

from app.config import settings
from app.utils.database import init_db
from app.api import models, testcases, debug, batch, tools, vl, system_prompts, training_data

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()  # 输出到控制台
    ]
)

# 获取logger
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # Startup
    logger.info(f"🚀 {settings.APP_NAME} v{settings.APP_VERSION} starting...")
    init_db()
    logger.info(f"✅ Database initialized at {settings.DATABASE_URL}")
    logger.info(f"📁 Results directory: {settings.RESULTS_DIR}")
    yield
    # Shutdown
    logger.info("Shutting down...")


# 创建FastAPI应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="大模型测试工具API",
    lifespan=lifespan
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册API路由
app.include_router(models.router, prefix="/api/models", tags=["models"])
app.include_router(testcases.router, prefix="/api/testcases", tags=["testcases"])
app.include_router(debug.router, prefix="/api/debug", tags=["debug"])
app.include_router(batch.router, prefix="/api/batch", tags=["batch"])
app.include_router(tools.router, prefix="/api/tools", tags=["tools"])
app.include_router(vl.router, prefix="/api/vl", tags=["vl"])
app.include_router(system_prompts.router, prefix="/api/system-prompts", tags=["system-prompts"])
app.include_router(training_data.router, prefix="/api/training-data", tags=["training-data"])


@app.get("/api/health")
async def health_check():
    """健康检查"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


# 挂载静态文件（前端）- 必须在所有API路由之后
frontend_path = Path(__file__).parent.parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/", StaticFiles(directory=str(frontend_path), html=True), name="frontend")


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level="info"  # 确保uvicorn使用info级别
    )
