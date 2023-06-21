import io
import uuid
from fastapi_router_controller import Controller
from fastapi.responses import ORJSONResponse, StreamingResponse
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
)

from app.api.core.config import get_settings
from app.api.core.security import authenticate_user
from app.api.core.observability import logger
from app.api.database.schema import DocumentosShema
from app.api.service.documento_service import start_update_one_documento, inativar_documento, expurgar_documentos_por_data
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.database.repository.documentos_repository import get_all_documentos, get_documento_by_uuid, get_documento_by_id, get_documento_by_area
from app.api.database.database import get_db
from app.api.service.generic_service import check_area, check_documento_exist, client_s3
from app.api.database.model import StatusTypes

settings = get_settings()

router = APIRouter()
controller = Controller(router, openapi_tag="DocumentosController")


@controller.resource()
class DocumentosController:
    
    def __init__(self, db: AsyncSession = Depends(get_db), client = Depends(client_s3)) :
        self.db = db
        self.client = client
    
    @controller.route.get(
        "/documentos",
        status_code=status.HTTP_200_OK,
        response_model=list[DocumentosShema],
    )
    async def get_all_documentos(
        self
    ) -> list[DocumentosShema]:
        return await get_all_documentos(self.db)


    @controller.route.get(
        "/documento/id/{id}",
        status_code=status.HTTP_200_OK,
        response_model=DocumentosShema,
    )
    async def find_documento_by_id(
        self, id: int
    ) -> DocumentosShema:
        return await get_documento_by_id(self.db, id)


    @controller.route.get(
        "/documento/area/{area}",
        status_code=status.HTTP_200_OK,
        response_model=list[DocumentosShema],
    )
    async def find_documento_by_area(
        self, area: str
    ) -> list[DocumentosShema]:
        documento = await get_documento_by_area(self.db, area)

        if documento is None:
            raise HTTPException(
                detail="Documento não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )

        return documento


    @controller.route.get(
        "/documento/doc_id/{doc_id}",
        status_code=status.HTTP_200_OK,
        response_model=DocumentosShema,
    )
    async def get_documento_doc_id(
        self, doc_id: uuid.UUID, 
    ) -> DocumentosShema:
        documento = await get_documento_by_uuid(self.db, doc_id)

        if documento is None:
            raise HTTPException(
                detail="Documento não encontrado", status_code=status.HTTP_404_NOT_FOUND
            )

        return documento


    @controller.route.post(
        "/documentos/{path_documento}", status_code=status.HTTP_201_CREATED
    )
    async def upload_one_documento(
        self,
        path_documento: str,
        background_tasks: BackgroundTasks,
        area_request: Annotated[str | None, Header()],
        token: Annotated[str | None, Header()],
        flag_token: bool = Depends(authenticate_user),
        arq: UploadFile = File(...),
    ):
        try:
            my_uuid = uuid.uuid4()

            area = await check_area(self.db, area_request, token)
            # await check_documento_exist(self.db, arq.filename)

            documento_upload = await start_update_one_documento(path_documento, area, self.db, arq, my_uuid)

            ret = {"message": "Arquivo Salvo no S3", "id_doc": str(my_uuid)}
            
            extra = {"tags": { "area": area_request} }
            
            logger.info("Arquivo Salvo", extra=extra)
            return ORJSONResponse(
                content=jsonable_encoder(ret), status_code=status.HTTP_201_CREATED
            )
        except HTTPException as ex:
            raise HTTPException(status_code=ex.status_code, detail=ex.detail)


    @controller.route.put("/documento/inativa/{doc_id}")
    async def inativa_documento(
        self,
        doc_id: uuid.UUID,
        area_request: Annotated[str | None, Header()],
        token: Annotated[str | None, Header()],
    ):
        try:
            area = await check_area(self.db, area_request, token)
            doc = await get_documento_by_uuid(self.db, doc_id)
            
            if doc is None:
                raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND,
                        detail="documento nao encontrado")
                
            if doc.status_documento == StatusTypes.ativo.name:
                flag_inativo = await inativar_documento(db=self.db, doc=doc)    
           
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
        self
    ):
        try:
            flag_expurgo = await expurgar_documentos_por_data(db=self.db)

            if flag_expurgo is True:
                message = "Expurgo Realizado"
            else: message = "Não existem documentos para expurgo"

            return ORJSONResponse(content=message, status_code=status.HTTP_200_OK)
        except HTTPException as ex:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="problema no expurgo")


    @controller.route.post("/documento/downloads/{id_doc}")
    async def downloads_documento(self, 
                                  id_doc: uuid.UUID):
                                #   area_request: Annotated[str | None, Header()],
                                #   token: Annotated[str | None, Header()]):
        
        documento = await get_documento_by_uuid(self.db, id_doc)
        
        if documento is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Documento não existe existente"),
            )
            
        result = self.client.download_file(settings.bucket_s3, f"/{documento.caminho_documento}", documento.nome_documento)
        
        # Criando um objeto de fluxo de bytes
        file_like = io.BytesIO(result["Body"].read())
        
        headers = {
            "Content-Disposition": "attachment; filename=exemplo.txt"
        }
        
        return StreamingResponse(file_like, headers=headers, media_type="application/octet-stream")
