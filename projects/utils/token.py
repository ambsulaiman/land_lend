import jwt
from jwt.exceptions import InvalidTokenError
from fastapi import HTTPException
from datetime import datetime, timedelta, timezone
import os

ACCESS_TOKEN_KEY = os.getenv('ACCESS_TOKEN_KEY', 'e9623a04fd79f49dd476f00ef4d4200209c147b83dc5db410d0d66500ef77beb')
TOKEN_EXPIRE_MINUTES = os.getenv('EXPIRE_TIME_DELTA', 60)
ALGORITHM = os.getenv('ALGORITHM', 'HS256')

def create_access_token(data: dict, expire_delta=timedelta(minutes=TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()

    exp = datetime.now(timezone.utc) + expire_delta
    to_encode.update({'exp': exp})

    return jwt.encode(to_encode, ACCESS_TOKEN_KEY, algorithm=ALGORITHM)

def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, key=ACCESS_TOKEN_KEY, algorithms=[ALGORITHM])
    except InvalidTokenError:
        raise HTTPException(status_code=405, detail='Token invalid or expired.')
    
    return payload