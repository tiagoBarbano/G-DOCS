
from pydantic import BaseSettings, PostgresDsn, AnyUrl, SecretStr, RedisDsn
from functools import lru_cache
from fastapi_cache import FastAPICache
from fastapi import Request, Response



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
    redis_url: RedisDsn
    
    class Config:
        env_file = ".env"
       
@lru_cache()        
def get_settings():
    return Settings()


def key_user_by_area(
    func,
    namespace: str | None = "",
    request: Request = None,
    response: Response = None,
    *args,
    **kwargs,
):
    user_name = kwargs["args"][1]
    prefix = FastAPICache.get_prefix()
    cache_key = f"{prefix}:{func.__name__}:{user_name}"
    return cache_key