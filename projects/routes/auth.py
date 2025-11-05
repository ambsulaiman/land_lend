from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import Session, select
from ..utils.token import create_access_token
from ..schemas.models import User, Token
from ..utils.security import verify_password_hash
from ..database import get_session


router = APIRouter(
    prefix='/auth',
    tags=['User Authentication route.']
)

@router.post(
    '/token',
    response_model=Token
)
async def login(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	session: Annotated[Session, Depends(get_session)]
):
    credential_exception = HTTPException(
        status_code=401,
        detail='Incorrect username or password',
        headers={'WWW-Authentication': 'Bearer'}
    )

    db_user = session.exec(
		select(User).where(User.email == form_data.username)
	).first()

    if not db_user:
        raise credential_exception

    if not verify_password_hash(form_data.password, db_user.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect username or password')

    data = {'sub': db_user.email}
    token = create_access_token(data=data)

    return Token(access_token=token, token_type='bearer')
