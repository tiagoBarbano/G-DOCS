import uuid, time
from fastapi_router_controller import Controller
from fastapi.responses import ORJSONResponse
from fastapi.encoders import jsonable_encoder
from fastapi import (
    HTTPException,
    status,
    APIRouter,
    Header,
    File,
    UploadFile,
    BackgroundTasks,
    Depends,
    Response,
)
from ..database.schema import DocumentosShema
from ..service.documento_service import add_new_documento, inativar_documento
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.repository.documentos_repository import (
    get_all_documentos,
    get_documento_by_uuid,
    get_documento_by_id,
    get_documento_by_area,
)
from ..database.database import get_db
from ..core.observability import logs


router = APIRouter()
controller = Controller(router)

global log
logger = logs()

@controller.resource()
class DocumentosController:
    @controller.route.get(
        "/v1/documentos",
        status_code=status.HTTP_200_OK,
        response_model=list[DocumentosShema],
    )
    async def get_all_documentos(
        self, db: AsyncSession = Depends(get_db)
    ) -> list[DocumentosShema]:
        return await get_all_documentos(db)

    @controller.route.get(
        "/v1/documento/id/{id_doc}",
        status_code=status.HTTP_200_OK,
        response_model=DocumentosShema,
    )
    async def get_documento(
        self, id_doc: int, db: AsyncSession = Depends(get_db)
    ) -> DocumentosShema:
        return await get_documento_by_id(db, id_doc)

    @controller.route.get(
        "/v1/documento/area/{area}",
        status_code=status.HTTP_200_OK,
        response_model=list[DocumentosShema],
    )
    async def get_documento(
        self, area: str, db: AsyncSession = Depends(get_db)
    ) -> list[DocumentosShema]:
        documento = await get_documento_by_area(db, area)

        if documento is None:
            raise HTTPException(
                detail="Documento não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )

        return documento

    @controller.route.get(
        "/v1/documento/uuid/{uuid}",
        status_code=status.HTTP_200_OK,
        response_model=DocumentosShema,
    )
    async def get_documento_uuid(
        self, uuid: uuid.UUID, db: AsyncSession = Depends(get_db)
    ) -> DocumentosShema:
        documento = await get_documento_by_uuid(db, uuid)

        if documento is None:
            raise HTTPException(
                detail="Documento não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )

        return documento

    @controller.route.post(
        "/v1/documentos/{path_documento}", status_code=status.HTTP_201_CREATED
    )
    async def create_documento(
        self,
        path_documento: str,
        background_tasks: BackgroundTasks,
        response: Response,
        area: Annotated[str | None, Header()],
        token: Annotated[str | None, Header()],
        db: AsyncSession = Depends(get_db),
        arq: UploadFile = File(...),
    ):
        try:
            start_time = time.time()
            my_uuid = uuid.uuid4()

            # background_tasks.add_task(
            #     add_new_documento, path_documento, area, token, db, arq, my_uuid
            # )
            
            ret = await add_new_documento(path_documento, area, token, db, arq, my_uuid)
            process_time = time.time() - start_time
            response.headers["process_time"] = str(process_time)

            logger.info("TEste")

            return ORJSONResponse(
                content=jsonable_encoder(ret), status_code=status.HTTP_201_CREATED
            )
        except HTTPException as ex:
            raise HTTPException(
                status_code=ex.status_code,
                detail=ex.detail
            )

    @controller.route.put("/v1/documento/inativa/{uuid}")
    async def inativa_documento(
        self,
        uuid: uuid.UUID,
        area: Annotated[str | None, Header()],
        token: Annotated[str | None, Header()],
        db: AsyncSession = Depends(get_db),
    ):
        try:
            documento = await inativar_documento(uuid, db, area, token)

            if documento is False:
                raise HTTPException(
                    detail="Problema na Atualização",
                    status_code=status.HTTP_400_BAD_REQUEST,
                )

            return ORJSONResponse(content=documento, status_code=status.HTTP_200_OK)
        except HTTPException as ex:
            raise HTTPException(
                status_code=ex.status_code,
                detail=ex.detail
            )


    @controller.route.post("/v1/documento/expurgo")
    async def expurgo_documento(
        self,
        area: Annotated[str | None, Header()],
        token: Annotated[str | None, Header()],
        db: AsyncSession = Depends(get_db),
    ):
        return ORJSONResponse(status_code=status.HTTP_501_NOT_IMPLEMENTED)