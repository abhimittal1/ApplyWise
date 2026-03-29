from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import get_settings
from app.core.database import check_db_connection
from app.api.v1 import auth, documents, knowledge, jobs, matching, generate, tracker, prep

settings = get_settings()

app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_PREFIX)
app.include_router(documents.router, prefix=settings.API_V1_PREFIX)
app.include_router(knowledge.router, prefix=settings.API_V1_PREFIX)
app.include_router(jobs.router, prefix=settings.API_V1_PREFIX)
app.include_router(matching.router, prefix=settings.API_V1_PREFIX)
app.include_router(generate.router, prefix=settings.API_V1_PREFIX)
app.include_router(tracker.router, prefix=settings.API_V1_PREFIX)
app.include_router(prep.router, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "CareerOS API",
        "version": "0.1.0",
        "docs": "/api/docs",
        "health": "/api/health",
        "api_prefix": settings.API_V1_PREFIX,
    }


@app.get("/api/health")
async def health_check():
    """Comprehensive health check including database connectivity"""
    db_healthy = await check_db_connection()

    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "app": settings.APP_NAME,
        "database": "connected" if db_healthy else "disconnected",
    }
