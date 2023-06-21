from fastapi.security import OAuth2PasswordBearer
from pydantic import ValidationError
from fastapi import Depends, HTTPException, status
import jwt



with open("openssl/jwt-key-public.pem", "r") as key_file:
    public_key = key_file.read()

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)


async def authenticate_user(token: str = Depends(oauth2_scheme)):
    authenticate_value = f"Bearer"
    try:
        payload = jwt.decode(token, public_key, algorithms=["RS256"])
        return True
    except (jwt.DecodeError, ValidationError, jwt.exceptions.ExpiredSignatureError) as ex:
        credentials_exception = await mount_error(
            authenticate_value=authenticate_value, ex=str(ex)
        )
        raise credentials_exception
              
    
async def mount_error(authenticate_value, ex):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Could not validate credentials: {ex}",
        headers={"WWW-Authenticate": authenticate_value},
    )