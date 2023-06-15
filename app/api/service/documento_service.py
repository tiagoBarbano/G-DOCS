import datetime, os
from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from botocore.exceptions import BotoCoreError, ClientError
from ..database.schema import DocumentosShema
from ..database.repository.documentos_repository import (
    add_documento,
    get_documento_by_data_criacao,
    update_documento,
    delete_documento,
)
from ..database.model import DocumentoModel, StatusTypes
from ..database.repository.area_repository import get_area_by_name
from ..core.config import get_settings
from .generic_service import client_s3
from ..core.observability import logger

settings = get_settings()


async def add_new_documento(path_documento, area, db, documento, myuuid):
    try:
        client = await client_s3()
        data_criacao = datetime.datetime.now()
        caminho_documento = f"{area.caminho_area}/{path_documento}/{documento.filename}"      

        res = os.path.join(os.getcwd(), "downloads")
        if not os.path.isdir(res):
            os.mkdir(res)

        os.chdir(res)
        file_location = f"{res}/{documento.filename}"

        with open(file_location, "wb+") as file_object:
            file_object.write(documento.file.read())

        client.upload_file(file_location, settings.bucket_s3, caminho_documento)
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

        extra = { "tags": doc_created.dict() }

        logger.info(msg=f"Arquivo salvo na base de dados", extra={'tags': jsonable_encoder(extra) })
    except (BotoCoreError, ClientError) as e:
        client.delete_object(Bucket=settings.bucket_s3, Key=file_location)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str("Token Incorreto"),
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
    
    extra = { "lista_expurgo": doc_schema.dict() }
    
    if flag_del:
        logger.info("Expurgo Realizado", extra={ 'tags': extra })
    
    return True

# @router.post("/enviar-arquivo-sinapse", status_code=status.HTTP_200_OK)
# async def enviar_arquivo_sinapse(arquivo):
#     logging.info('### Início ###')
#     try:
#         s3 = boto3.resource(
#             service_name=service_name,
#             aws_access_key_id=access_key,
#             aws_secret_access_key=access_secret,
#             region_name=region_name
#         )
#         copy_source = {
#             'Bucket': bucket_name,
#             'Key': f"{path_renovacao}/{arquivo}"
#         }

#         s3.meta.client.copy(copy_source, bucket_name,
#                             f"{path_salva}/{arquivo}")

#         s3.meta.client.copy(copy_source, bucket_name,
#                             f"{path_sinapse}/{arquivo}")

#         s3.meta.client.delete_object(
#             Bucket=bucket_name, Key=f"{path_renovacao}/{arquivo}")

#         logging.info('### Término - arquivo enviado ###')
#         return {"Status": "Sucesso",
#                 "Arquivo": arquivo,
#                 "Descricao": "Realizado o Upload do arquivo com sucesso para a pasta do Sinapse"}
#     except FileNotFoundError as err:
#         print(err)
#         return {"Status": "Error",
#                 "Arquivo": arquivo,
#                 "Descricao": err.strerror}
