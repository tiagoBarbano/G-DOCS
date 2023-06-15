import uuid, time, asyncio
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
from ..service.documento_service import add_new_documento, inativar_documento, expurgar_documentos_por_data
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from ..database.repository.documentos_repository import (
    get_all_documentos,
    get_documento_by_uuid,
    get_documento_by_id,
    get_documento_by_area,
)
from ..database.database import get_db
from ..core.observability import logger
from ..service.generic_service import check_area, check_documento_exist
from ..database.model import StatusTypes


router = APIRouter()
controller = Controller(router, openapi_tag="DocumentosController")


@controller.resource()
class DocumentosController:
    @controller.route.get(
        "/documentos",
        status_code=status.HTTP_200_OK,
        response_model=list[DocumentosShema],
    )
    async def get_all_documentos(
        self, db: AsyncSession = Depends(get_db)
    ) -> list[DocumentosShema]:
        return await get_all_documentos(db)

    @controller.route.get(
        "/documento/id/{id_doc}",
        status_code=status.HTTP_200_OK,
        response_model=DocumentosShema,
    )
    async def get_documento(
        self, id_doc: int, db: AsyncSession = Depends(get_db)
    ) -> DocumentosShema:
        return await get_documento_by_id(db, id_doc)

    @controller.route.get(
        "/documento/area/{area}",
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
        "/documento/uuid/{uuid}",
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
        "/documentos/{path_documento}", status_code=status.HTTP_201_CREATED
    )
    async def create_documento(
        self,
        path_documento: str,
        background_tasks: BackgroundTasks,
        response: Response,
        area_request: Annotated[str | None, Header()],
        token: Annotated[str | None, Header()],
        db: AsyncSession = Depends(get_db),
        arq: UploadFile = File(...),
    ):
        try:
            my_uuid = uuid.uuid4()

            area = await check_area(db, area_request, token)
            flag_doc = await check_documento_exist(db, arq.filename)

            background_tasks.add_task(
                add_new_documento, path_documento, area, db, arq, my_uuid
            )
            
            ret = {"message": "Solicitação em processamento", "id_doc": str(my_uuid)}

            return ORJSONResponse(
                content=jsonable_encoder(ret), status_code=status.HTTP_201_CREATED
            )
        except HTTPException as ex:
            raise HTTPException(status_code=ex.status_code, detail=ex.detail)

    @controller.route.put("/documento/inativa/{uuid}")
    async def inativa_documento(
        self,
        uuid: uuid.UUID,
        area_request: Annotated[str | None, Header()],
        token: Annotated[str | None, Header()],
        db: AsyncSession = Depends(get_db),
    ):
        try:
            area = await check_area(db, area_request, token)
            doc = await get_documento_by_uuid(db, uuid)
            
            if doc is None:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="documento nao encontrado")
                
            if doc.status_documento == StatusTypes.ativo.name:
                flag_inativo = await inativar_documento(db=db, doc=doc)    
           
                if flag_inativo is False:
                    raise HTTPException(
                        detail="Problema na Atualização",
                        status_code=status.HTTP_400_BAD_REQUEST,
                    )

                ret = { 
                        "message": "Documento Inativado com Sucesso",
                        "id_doc": uuid,
                        }
            else:
                ret = { 
                        "message": "Documento Não pode ser Inativado: Status diferente de Ativo",
                        "id_doc": uuid,
                        }
                
            return ORJSONResponse(content=ret, status_code=status.HTTP_200_OK)
        except HTTPException as ex:
            raise HTTPException(status_code=ex.status_code, detail=ex.detail)

    @controller.route.post("/documento/expurgo")
    async def expurgo_documento(
        self,
        db: AsyncSession = Depends(get_db),
    ):
        try:
            flag_expurgo = await expurgar_documentos_por_data(db=db)

            if flag_expurgo is True:
                message = "Expurgo Realizado"
            else: message = "Não existem documentos para expurgo"

            return ORJSONResponse(content=message, status_code=status.HTTP_200_OK)
        except HTTPException as ex:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="problema no expurgo")
