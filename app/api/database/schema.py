from uuid import UUID
from pydantic import BaseModel, Field
from datetime import datetime
from .model import StatusTypes


class DocumentosShema(BaseModel):
    id: None | int
    area_responsavel: str = Field(...)
    my_uuid: UUID = Field(...)
    nome_documento: str = Field(...)
    caminho_documento: str = Field(...)
    status_documento: StatusTypes = Field(...)
    data_criacao: datetime = Field(...)
    data_atualizacao: datetime = Field(...)
    data_inativacao: datetime = Field(...)
    
    class Config:
        orm_mode = True
        
class AreaShema(BaseModel):
    id: None | int
    nome_area: str = Field(...)
    token_area: None | str = Field(...)
    caminho_area: str = Field(...)
    status_area: StatusTypes = Field(...)
    data_criacao: datetime = Field(...)
    data_atualizacao: datetime = Field(...)
    data_inativacao: datetime = Field(...)
    
    class Config:
        orm_mode = True
        
class AreaRequestShema(BaseModel):
    nome_area: str = Field(...)
    
