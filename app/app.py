from typing import Any
from app.api.controller.documentos_controllers import DocumentosController
from app.api.controller.area_controllers import AreaController
from fastapi import FastAPI
from app.api.core.observability import metrics, tracing, logs
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

    global log
    logger = logs()
      	
    metrics(app=app)
    tracing(app=app,engine=engine)

    app.include_router(DocumentosController.router())
    app.include_router(AreaController.router())
    
    return app
