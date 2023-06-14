import boto3
from fastapi import HTTPException, status
from ..core.config import get_settings
from ..database.repository.area_repository import get_area_by_name
from ..database.repository.documentos_repository import get_documento_by_name

settings = get_settings()


async def client_s3():
    return boto3.client(
        service_name=settings.service_name,
        aws_access_key_id=settings.access_key.get_secret_value(),
        aws_secret_access_key=settings.access_secret.get_secret_value(),
        region_name=settings.region_name,
    )
    
async def check_area(db, area, token):
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
    
    return find_area

async def check_documento_exist(db, filename):
    doc = await get_documento_by_name(db, filename)
    
    if doc is not None:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=str("Documento já existente"),
            )     
    
    return True