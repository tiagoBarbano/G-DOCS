import boto3
from ..core.config import get_settings

settings = get_settings()


async def client_s3():
    return boto3.client(
        service_name=settings.service_name,
        aws_access_key_id=settings.access_key.get_secret_value(),
        aws_secret_access_key=settings.access_secret.get_secret_value(),
        region_name=settings.region_name,
    )