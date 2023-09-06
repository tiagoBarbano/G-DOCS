from typing import Any
from app.api.controller.documentos_controllers import DocumentosController
from app.api.controller.area_controllers import AreaController
from fastapi import FastAPI
from app.api.core.observability import metrics, tracing
from app.api.database.database import engine
from redis import asyncio as aioredis
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from app.api.core.config import get_settings

settings = get_settings()


def create_app():
    app: Any = FastAPI(
        title="Estudo Python",
        description="Integracao com DB SQL",
        version="1.0.0",
        openapi_url="/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    metrics(app=app)
    tracing(app=app,engine=engine)
    
    async def on_startup() -> None:
        redis = aioredis.from_url(settings.redis_url,
                                  encoding="utf-8",
                                  decode_responses=True)
        FastAPICache.init(RedisBackend(redis), prefix="oauth")
    
    
    app.add_event_handler("startup", on_startup)
    app.include_router(DocumentosController.router(), tags=["DocumentosController"], prefix="/v1")
    app.include_router(AreaController.router(), tags=["AreaController"], prefix="/v1")
    
    return app
