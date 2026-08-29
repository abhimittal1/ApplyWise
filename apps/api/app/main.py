from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.config import get_settings
from app.core.database import check_db_connection
from app.core.rate_limit import check_redis_connection, close_redis_client
from app.api.v1 import auth, documents, knowledge, jobs, matching, generate, tracker, prep

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await close_redis_client()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
)

# Session middleware for OAuth state & CSRF protection
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
    same_site="lax",
    https_only=not settings.DEBUG,
)

# CORS middleware with strict origin controls
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=settings.CORS_ORIGIN_REGEX if settings.CORS_ORIGIN_REGEX else None,
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
    """Comprehensive health check including database and Redis connectivity"""
    db_healthy = await check_db_connection()
    redis_healthy = await check_redis_connection()

    overall_healthy = db_healthy and (redis_healthy or not settings.REDIS_URL)

    return {
        "status": "healthy" if overall_healthy else "unhealthy",
        "app": settings.APP_NAME,
        "database": "connected" if db_healthy else "disconnected",
        "redis": "connected" if redis_healthy else "disconnected",
    }
