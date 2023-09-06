import datetime
import os
from boto3.s3.transfer import TransferConfig
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from botocore.exceptions import BotoCoreError, ClientError
from app.api.database.schema import DocumentosShema
from app.api.database.repository.documentos_repository import add_documento, get_documento_by_data_criacao, update_documento,delete_documento
from app.api.database.model import DocumentoModel, StatusTypes
from app.api.core.config import get_settings
from app.api.service.generic_service import client_s3
from app.api.core.observability import logger

settings = get_settings()
# client = client_s3()


async def start_update_one_documento(path_documento, area, db, documento, myuuid):
    try:
        data_criacao = datetime.datetime.now()
        config = TransferConfig(
            multipart_threshold=1024 * 50,
            max_concurrency=10,
            multipart_chunksize=1024 * 50,
            use_threads=True,
        )
        caminho_documento = f"{area.caminho_area}/{path_documento}/{documento.filename}"

        res = os.path.join(os.getcwd(), "downloads")
        if not os.path.isdir(res):
            os.mkdir(res)

        os.chdir(res)
        file_location = f"{res}/{documento.filename}"

        with open(file_location, "wb+") as file_object:
            file_object.write(documento.file.read())

        # client.upload_file(
        #     file_location, settings.bucket_s3, caminho_documento, Config=config
        # )
        os.remove(file_location)

        logger.info("Arquivo salvo no S3")

        new_doc = DocumentoModel(
            area_responsavel=area.nome_area,
            my_uuid=myuuid,
            nome_documento=documento.filename,
            caminho_documento=caminho_documento,
            status_documento=StatusTypes.ativo.name,
            data_criacao=data_criacao,
            data_atualizacao=data_criacao,
            data_inativacao=datetime.datetime(2999, 12, 31),
        )

        doc_created = await add_documento(db, new_doc)

        extra = {"tags": jsonable_encoder(doc_created)}

        logger.info(
            msg="Arquivo salvo na base de dados",
            extra={"tags": jsonable_encoder(extra)},
        )
        
        return jsonable_encoder(doc_created)
    except (BotoCoreError, ClientError, Exception) as ex:
        # client.delete_object(Bucket=settings.bucket_s3, Key=file_location)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(f"Token Incorreto: {str(ex)}"),
        )


async def inativar_documento(db, doc):
    doc.status_documento = StatusTypes.inativo.name

    doc_schema = DocumentosShema.from_orm(doc)

    flag_update = await update_documento(db, doc.id, doc_schema.dict())

    return flag_update


async def expurgar_documentos_por_data(db):
    delta_data_expurgo = datetime.timedelta(settings.qtd_dias_expurgo)
    data_expurgo = datetime.datetime.now() - delta_data_expurgo

    doc = await get_documento_by_data_criacao(db=db, data_expurgo=data_expurgo)

    if not doc:
        logger.info("Não existem documentos para expurgo")
        return False

    doc_schema = DocumentosShema.from_orm(doc)

    ids = [y.id for y in doc]

    flag_del = await delete_documento(db=db, ids=ids)

    extra = {"lista_expurgo": doc_schema.dict()}

    if flag_del:
        logger.info("Expurgo Realizado", extra={"tags": extra})

    return True
