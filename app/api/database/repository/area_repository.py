from app.api.database.schema import AreaShema
from app.api.database.model import AreaModel
from sqlalchemy import update, delete
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession


async def get_all_areas(db: AsyncSession):
    query = select(AreaModel)
    areas = await db.execute(query)
    areas = areas.scalars().all()
    return areas


async def get_area_by_id(db: AsyncSession, id: int) -> dict:
    query = select(AreaModel).where(AreaModel.id == id)
    areas = await db.execute(query)
    area = areas.scalar_one_or_none()
    return area


async def get_area_by_name(db: AsyncSession, nome_area: str) -> dict:
    q = select(AreaModel).where(AreaModel.nome_area == nome_area) 
    areas = await db.execute(q)
    area = areas.scalar_one_or_none()
    return area


async def add_area(db: AsyncSession, area: AreaShema) -> AreaShema:

    new_area = AreaModel(nome_area=area.nome_area,
                         token_area=area.token_area,
                         caminho_area=area.caminho_area,
                         status_area=area.status_area,
                         data_criacao=area.data_criacao,
                         data_atualizacao=area.data_atualizacao)

    db.add(new_area)
    return new_area


async def update_area(db: AsyncSession, id: str, data: AreaShema):
    query = (update(AreaModel).where(AreaModel.id == id).values(data).execution_options(synchronize_session="fetch"))
    await db.execute(query)


async def delete_area(db: AsyncSession, id: int):
    query = delete(AreaModel).where(AreaModel.id == id)
    await db.execute(query)
    try:
        await db.commit()
    except Exception:
        await db.rollback()
        raise
    return True