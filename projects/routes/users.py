from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, Form
from sqlmodel import select, Session
from ..schemas.models import User, UserIn, UserOut, UserUpdate, UserAdminUpdate, UserOutWithLands
from ..schemas.enums import RoleEnum
from ..database import get_session
from ..utils.security import (
			get_password_hash,
			get_current_active_user,
			authorize_user
)


router = APIRouter(
    prefix='/users'
)


@router.post('/')
async def register_user(
	user: UserIn,
	session: Annotated[Session, Depends(get_session)]
):
	db_user = session.exec(
		select(User).where(User.email == user.email)
	).first()

	if db_user:
		raise HTTPException(status_code=400, detail='User already registered, consider changing the email')

	hashed_password = get_password_hash(user.password)

	new_user = User.model_validate(user, update={'hashed_password': hashed_password, 'role': RoleEnum.admin}) # 'role': RoleEnum.admin

	session.add(new_user)
	session.commit()

	return {'msg': 'User registered successfully', 'ok': True}

@router.get('/me', response_model=UserOutWithLands)
async def get_user(
	user: Annotated[User, Depends(get_current_active_user)]
):
	return user

@router.get('/{user_id}', response_model=UserOutWithLands)
async def get_user(
	user_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
	session: Annotated[Session, Depends(get_session)]
):
	if user_id != user.id and user.role != RoleEnum.admin:
		raise HTTPException(status_code=405, detail='Not authorized.')
	
	db_user = session.get(User, user_id)
	if not db_user:
		raise HTTPException(status_code=404, detail=f'User with id={user_id} not found.')
	return db_user

@router.get('/', dependencies=[Depends(authorize_user(RoleEnum.admin))], response_model=list[UserOutWithLands])
async def get_users(*,
	skip: int = 0,
	limit: int = 100,
	session: Annotated[Session, Depends(get_session)]
):
	db_users = session.exec(
		select(User).offset(skip).limit(limit)
	).all()

	if not db_users:
		raise HTTPException(status_code=404, detail='No user registered.')
	
	return db_users

@router.patch('/', response_model=UserOut)
async def user_update(
	user: Annotated[User, Depends(get_current_active_user)],
	update_data: UserUpdate,
	session: Annotated[Session, Depends(get_session)]
):
	extra = {}
	if update_data.password:
		extra['hashed_password'] = get_password_hash(update_data.password)

	update_data = User.model_dump(update_data, exclude_unset=True)

	user.sqlmodel_update(update_data, update=extra)

	session.add(user)
	session.commit()

	session.refresh(user)

	return user

@router.put('/', response_model=UserOut, dependencies=[Depends(get_current_active_user)])
async def user_update(
	user_id: int,
	update_data: UserAdminUpdate,
	session: Annotated[Session, Depends(get_session)]
):
	user = session.get(User, user_id)

	if not user:
		raise HTTPException(status_code=404, detail='User not found.')

	update_data = User.model_dump(update_data, exclude_unset=True)

	user.sqlmodel_update(update_data)

	session.add(user)
	session.commit()

	session.refresh(user)

	return user

@router.delete('/', response_model=dict[str, str | bool])
async def delete_user(
	user: Annotated[User, Depends(get_current_active_user)],
	session: Annotated[Session, Depends(get_session)]
):
	session.delete(user)
	session.commit()

	return {'msg': 'Deleted successfully!.', 'ok': True}

@router.delete('/users/{user_id}', response_model=dict[str, str | bool], dependencies=[Depends(get_current_active_user)])
async def delete_user(
	user_id: int,
	session: Annotated[Session, Depends(get_session)]
):
	user = session.get(User, user_id)
	if not user:
		raise HTTPException(status_code=404, detail='User not found.')

	session.delete(user)
	session.commit()

	return {'msg': f'Deleted user with id={user_id} successfully!.', 'ok': True}