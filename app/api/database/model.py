from sqlalchemy import Column, String, Integer, UUID, DateTime, Enum
from sqlalchemy.orm import declarative_base
import enum


class StatusTypes(str, enum.Enum):
    ativo = "ativo"
    inativo = "inativo"
    excluido = "excluido"
    vencido = "vencido"
    pendente = "pendente"


Base = declarative_base()


class DocumentoModel(Base):
    __tablename__ = "documento"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    area_responsavel = Column(String, index=True)
    my_uuid = Column(UUID, index=True)
    nome_documento = Column(String, index=True)
    caminho_documento = Column(String)
    status_documento = Column(Enum(StatusTypes), index=True)
    data_criacao = Column(DateTime)
    data_atualizacao = Column(DateTime)
    data_inativacao = Column(DateTime)


class AreaModel(Base):
    __tablename__ = "area"

    id = Column(Integer, autoincrement=True, primary_key=True, index=True)
    nome_area = Column(String, index=True)
    token_area = Column(String)
    caminho_area = Column(String)
    status_area = Column(Enum(StatusTypes), index=True)
    data_criacao = Column(DateTime)
    data_atualizacao = Column(DateTime)
