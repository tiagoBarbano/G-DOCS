import datetime
from uuid import UUID
from app.api.database.schema import DocumentosShema
from app.api.database.model import DocumentoModel, StatusTypes
from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.core.config import key_user_by_area
from fastapi_cache.decorator import cache
from fastapi_cache.coder import JsonCoder


async def get_all_documentos(db: AsyncSession):
    query = select(DocumentoModel)
    documentos = await db.execute(query)
    documentos = documentos.scalars().all()
    return documentos


async def get_documento_by_id(db: AsyncSession, id: int) -> dict:
    query = select(DocumentoModel).where(DocumentoModel.id == id)
    documentos = await db.execute(query)
    documento = documentos.scalar_one_or_none()
    return documento

@cache(expire=60,
       coder=JsonCoder,
       key_builder=key_user_by_area)
async def get_documento_by_area(db: AsyncSession, area: str) -> dict:
    q = select(DocumentoModel).where(DocumentoModel.area_responsavel == area) 
    documentos = await db.execute(q)
    documentos = documentos.scalars().all()
    return documentos


async def get_documento_by_name(db: AsyncSession, nome_documento: str) -> dict:
    q = select(DocumentoModel).where(DocumentoModel.nome_documento == nome_documento) 
    documentos = await db.execute(q)
    documento = documentos.scalar_one_or_none()
    return documento


async def get_documento_by_uuid(db: AsyncSession, uuid: UUID) -> dict:
    q = select(DocumentoModel).where(DocumentoModel.my_uuid == uuid) 
    documentos = await db.execute(q)
    documento = documentos.scalar_one_or_none()
    return documento


async def get_documento_by_uuid_status(db: AsyncSession, uuid: UUID, status: StatusTypes) -> dict:
    q = select(DocumentoModel).where(DocumentoModel.my_uuid == uuid).where(DocumentoModel.status_documento == status)
    documentos = await db.execute(q)
    documento = documentos.scalar_one_or_none()
    return documento


async def get_documento_by_data_criacao(db: AsyncSession, data_expurgo: datetime) -> dict:
    q = select(DocumentoModel).where(DocumentoModel.data_criacao < data_expurgo)
    documentos = await db.execute(q)
    documentos = documentos.scalars().all()
    return documentos


async def add_documento(db: AsyncSession, documento: DocumentosShema) -> DocumentosShema:
    new_documento = DocumentoModel(area_responsavel=documento.area_responsavel,
                         my_uuid=documento.my_uuid,
                         nome_documento=documento.nome_documento,
                         caminho_documento=documento.caminho_documento,
                         status_documento=documento.status_documento,
                         data_criacao=documento.data_criacao,
                         data_atualizacao=documento.data_atualizacao,
                         data_inativacao=documento.data_inativacao)

    db.add(new_documento)
    return new_documento


async def update_documento(db: AsyncSession, id: int, data: DocumentosShema):
    query = (update(DocumentoModel).where(DocumentoModel.id == id).values(data).execution_options(synchronize_session="fetch"))
    doc_update =await db.execute(query)
    
    if doc_update:
        await db.commit()
        return True

    return False

# Delete a documento from the database
async def delete_documento(db: AsyncSession, ids: list[int]):
    query = delete(DocumentoModel).filter(DocumentoModel.id.in_(ids))
    await db.execute(query)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return True