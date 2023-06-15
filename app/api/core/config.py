
from pydantic import BaseSettings, PostgresDsn, AnyUrl, SecretStr
from functools import lru_cache


class Settings(BaseSettings):
    asyncpg_url: PostgresDsn
    host_jaeger: str
    port_jaeger: int
    url_loki: AnyUrl
    app_name: str
    bucket_s3: str
    service_name:str
    access_key: SecretStr
    access_secret: SecretStr
    region_name: str
    otlp_url: AnyUrl
    qtd_dias_expurgo: int
    
    class Config:
        env_file = ".env"
       
@lru_cache()        
def get_settings():
    return Settings()
