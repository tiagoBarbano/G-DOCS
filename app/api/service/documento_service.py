import datetime, time, asyncio, os
from fastapi import HTTPException, status

from app.api.database.schema import DocumentosShema
from ..database.repository.documentos_repository import (
    add_documento,
    get_documento_by_uuid,
    get_documento_by_name,
    update_documento,
)
from ..database.model import DocumentoModel, StatusTypes
from ..database.repository.area_repository import *
from ..core.config import get_settings
from .generic_service import client_s3
from ..core.observability import logs

settings = get_settings()

logger = logs()

async def add_new_documento(path_documento, area, token, db, documento, myuuid):

    start_time = time.time()
    # find_area, doc = await asyncio.gather(get_area_by_name(db, area), 
    #                                       get_documento_by_name(db, documento.filename))
    
    find_area = await get_area_by_name(db, area)
    doc = await get_documento_by_name(db, documento.filename)

    if token != find_area.token_area:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Token Incorreto"),
            )

    if find_area is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Area não existe"),
            )

    if doc is not None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Documento já existente"),
            )     

    data_criacao = datetime.datetime.now()
    caminho_documento = (
        f"{find_area.caminho_area}/{path_documento}/{documento.filename}"
    )

    client = await client_s3()

    res = os.path.join(os.getcwd(), "downloads")
    if not os.path.isdir(res):
        os.mkdir(res)

    os.chdir(res)
    file_location = f"{res}/{documento.filename}"

    with open(file_location, "wb+") as file_object:
        file_object.write(documento.file.read())

    client.upload_file(file_location, settings.bucket_s3, caminho_documento)

    logger.info("Arquivo salvo no S3")
    
    new_doc = DocumentoModel(
        area_responsavel=area,
        my_uuid=myuuid,
        nome_documento=documento.filename,
        caminho_documento=caminho_documento,
        status_documento=StatusTypes.ativo.name,
        data_criacao=data_criacao,
        data_atualizacao=data_criacao,
        data_inativacao=datetime.datetime(2999, 12, 31),
    )

    doc_created = await add_documento(db, new_doc)

    process_time = time.time() - start_time
    print(str(process_time))
    os.remove(file_location)
    
    return doc_created


    
async def inativar_documento(uuid, db, area, token):
       
    find_area = await get_area_by_name(db, area)
    if token != find_area.token_area:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Token Incorreto"),
            )

    if find_area is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Area não existe"),
            )

    doc = await get_documento_by_uuid(db, uuid)
    if doc is None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Documento não encontrado"),
        )   

    if doc.status_documento == StatusTypes.inativo.name:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Documento já Inativado"),
            )
                   
    doc.status_documento = StatusTypes.inativo.name
    
    doc_schema = DocumentosShema.from_orm(doc)
    
    flag_update = await update_documento(db, doc.id, doc_schema.dict())

    return flag_update
    

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
