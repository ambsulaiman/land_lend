from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlmodel import Session, select
from ..database import get_session
from ..schemas.models import User
from ..schemas.enums import RoleEnum
from .token import create_access_token, decode_access_token


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/token')


password_hash = PasswordHash.recommended()


def get_password_hash(password: str) -> str:
    return password_hash.hash(password)

def verify_password_hash(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password)


###################
## authentication
###################

def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], session: Annotated[Session, Depends(get_session)]):
    payload = decode_access_token(token)
    email = payload.get('sub')
    db_user = session.exec(
        select(User).where(User.email == email)
    ).first()
    if not db_user:
        raise HTTPException(status_code=401, detail='Invalid token.')
    
    return db_user

def get_current_active_user(user: Annotated[User, Depends(get_current_user)]):
    if user.disabled:
        raise HTTPException(status_code=401, detail='User Inactive.')
    return user

def authorize_user(role_required: list[RoleEnum]):
    def require(user: Annotated[User, Depends(get_current_active_user)]):
        if user.role in role_required and user.role != RoleEnum.admin:
            raise HTTPException(status_code=405, detail='User authorize.')
        return user
    return require

