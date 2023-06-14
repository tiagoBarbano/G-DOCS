from fastapi_router_controller import Controller
from fastapi import HTTPException, status, APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from ..database.model import AreaModel, StatusTypes
from ..database.schema import AreaRequestShema, AreaShema
from ..database.repository.area_repository import get_area_by_name, add_area
from ..database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import ORJSONResponse
import datetime, secrets


router = APIRouter()
controller = Controller(router)

@controller.resource()
class AreaController:
    
    @controller.route.post("/area", response_model=AreaShema)
    async def create_area(self, area: AreaRequestShema, db: AsyncSession = Depends(get_db)):        
        find_area = await get_area_by_name(db, area.nome_area)
    
        if find_area:
            raise HTTPException(status_code=400, detail="area Exists!!!")
        
        caminho_area = f"dir_repo_{area.nome_area}_porto"
        token = secrets.token_hex(32)
        data_criacao = datetime.datetime.now()    
        new_area = AreaModel(nome_area=area.nome_area,
                            token_area=token,    
                            caminho_area=caminho_area,
                            status_area=StatusTypes.ativo.name,
                            data_criacao=data_criacao,    
                            data_atualizacao=data_criacao)
        
        area_created = await add_area(db, new_area)
        
        return ORJSONResponse(content=jsonable_encoder(area_created), status_code=status.HTTP_201_CREATED)