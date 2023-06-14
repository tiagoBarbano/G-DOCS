from typing import Any
from app.api.controller.documentos_controllers import DocumentosController
from app.api.controller.area_controllers import AreaController
from fastapi import FastAPI
from app.api.core.observability import metrics, tracing
from app.api.database.database import engine


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

    app.include_router(DocumentosController.router(), tags=["DocumentosController"], prefix="/v1")
    app.include_router(AreaController.router(), tags=["AreaController"], prefix="/v1")
    
    return app
