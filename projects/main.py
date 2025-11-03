# Bismillah

from typing import Annotated

from fastapi import FastAPI, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordRequestForm
from sqlmodel import select, Session, or_
from .schemas.models import User, UserIn, UserOut, UserUpdate, UserAdminUpdate, Land, LandIn, LandOut, LandUpdate, Chat, ChatIn, ChatOut, ChatUpdate
from .schemas.enums import RoleEnum
from .database import init_db, get_session
from .utils.token import create_access_token, decode_access_token
from .utils.security import (
			get_password_hash,
			verify_password_hash,
			get_current_active_user,
			get_current_user,
			authorize_user
)



app = FastAPI()


@app.on_event('startup')
async def startup():
	init_db()


################
## authetication
################

@app.post('/auth/token')
async def login(
	form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
	session: Annotated[Session, Depends(get_session)]
):
	db_user = session.exec(
		select(User).where(User.email == form_data.username)
	).first()

	if not db_user:
		raise HTTPException(status_code=401, detail='Incorrect username or password')

	if not verify_password_hash(form_data.password, db_user.hashed_password):
		raise HTTPException(status_code=401, detail='Incorrect username or password')
	
	data = {'sub': db_user.email}
	token = create_access_token(data=data)

	return {'access_token': token, 'token_type': 'bearer'}


@app.post('/users/')
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

	new_user = User.model_validate(user, update={'hashed_password': hashed_password})

	session.add(new_user)
	session.commit()

	return {'msg': 'User registered successfully', 'ok': True}

@app.get('/users/me', response_model=UserOut)
async def get_user(
	user: Annotated[User, Depends(get_current_active_user)]
):
	return user

@app.get('/users/{user_id}', response_model=UserOut)
async def get_user(
	user_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
	session: Annotated[Session, Depends(get_session)]
):
	if user_id != user.id and user.role != RoleEnum.admin:
		raise HTTPException(status_code=405, detail='Not authorized.')
	
	db_user = session.get(User, user_id)
	return db_user

@app.get('/users/', dependencies=[Depends(authorize_user(RoleEnum.admin))], response_model=list[UserOut])
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

@app.patch('/users/', response_model=UserOut)
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

@app.put('/users/', response_model=UserOut, dependencies=[Depends(get_current_active_user)])
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

@app.delete('/users/', response_model=dict[str, str | bool])
async def delete_user(
	user: Annotated[User, Depends(get_current_active_user)],
	session: Annotated[Session, Depends(get_session)]
):
	session.delete(user)
	session.commit()

	return {'msg': 'Deleted successfully!.', 'ok': True}



@app.post('/lands/', status_code=201, dependencies=[Depends(authorize_user([RoleEnum.admin]))])
async def register_land(land: Land, session: Annotated[Session, Depends(get_session)]):
	db_land = session.exec(
		select(Land).where(Land.name == land.name)
	).first()
	if db_land:
		raise HTTPException(status_code=404, detail='Land already registered, if not consider changing the name')

	session.add(land)
	session.commit()

@app.get('/lands/',
	dependencies=[
		Depends(
			authorize_user(
				[RoleEnum.normal_user,
				RoleEnum.security,
				RoleEnum.staff]
			)
		)
	],
	response_model=list[LandOut]
)
async def fetch_land_info(*,
	skip: int = 0,
	limit: int = 100,
	session: Annotated[Session, Depends(get_session)],
	address: str | None = None,
	location: str | None = None,
	size_lesser: int | None = None,
	size_greater: int | None = None,
	description: str | None = None,
):

	stmt = select(Land)

	if address:
		stmt = stmt.where(Land.address == address)
	if description:
		stmt = stmt.where(Land.description == description)
	if location:
		stmt = stmt.where(Land.location == location)
	if size_lesser:
		stmt = stmt.where(Land.size_lesser == size_lesser)
	if size_greater:
		stmt = stmt.where(size_greater == size_greater)
	
	lands = session.exec(
		stmt.offset(skip).limit(limit)
	).all()

	if not lands:
		raise HTTPException(status_code=404, detail='No Found!. Refresh the filter and reload')

	return lands

@app.patch('/lands/', dependencies=[Depends(authorize_user(RoleEnum.admin))], response_model=LandOut)
async def update_land_info(land_id:int, update_data: LandUpdate, session: Annotated[Session, Depends(get_session)]):
	land = session.get(Land, land_id)

	if not land:
		raise HTTPException(status_code=404, detail='Land not Found.')
	
	update_data = Land.model_dump(update_data, exclude_unset=True)

	land.sqlmodel_update(update_data)

	session.add(land)
	session.commit()
	
	session.refresh(land)

	return land

@app.delete('/lands/')
async def delete_land_info(
	land_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
	session: Annotated[Session, Depends(get_session)]
):
	land = session.get(Land, land_id)
	if land.id != user.id:
		raise HTTPException(status_code=404, detail='Not Found.')

	session.delete(land)
	session.commit()

	return {'msg': 'Land info successfully deleted!.', 'ok': True}

@app.post(
	'/chats/', 
	status_code=201,
	dependencies=[
		Depends(
			authorize_user(
				[RoleEnum.normal_user,
				RoleEnum.security,
				RoleEnum.staff]
			)
		)
	]
)
async def register_chat(
	chat: Chat,
	session: Annotated[Session, Depends(get_session)]
):
	
	session.add(chat)
	session.commit()

@app.get('/chats/', response_model=list[ChatOut])
async def fetch_chats(*,
	user: Annotated[User, Depends(get_current_active_user)],
	skip: int = 0, limit: int = 100,
	session: Annotated[Session, Depends(get_session)]
):
	chats = session.exec(
		select(Chat).where(or_(Chat.sender_id == user.id, Chat.intended_user == RoleEnum.All)).offset(skip).limit(limit)
	).all()

	if not chats:
		raise HTTPException(status_code=404, detail='No Chats yet!.')

	return chats

@app.post('/chats/broadcast/', status_code=201, dependencies=[Depends(authorize_user([RoleEnum.admin]))])
async def broadcast(*,
	chat: Chat,
	session: Annotated[Session, Depends(get_session)]
):
	chat.intended_user = RoleEnum.All

	session.add(chat)
	session.commit()

@app.patch('/chats/', response_model=ChatOut)
async def update_chat(
	chat_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
	update_data: ChatUpdate,
	session: Annotated[Session, Depends(get_session)]
):
	chat = session.get(Chat, chat_id)

	if chat.id != user.id:
		raise HTTPException(status_code=405, detail='Not authorize.')

	if not chat:
		raise HTTPException(status_code=404, detail='Chat not Found.')
	
	update_data = Chat.model_dump(update_data, exclude_unset=True)

	chat.sqlmodel_update(update_data)

	session.add(chat)
	session.commit()
	
	session.refresh(chat)

	return chat


@app.delete('/chats/')
async def delete_chat(
	chat_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
	session: Annotated[Session, Depends(get_session)]
):
	chat = session.get(Chat, chat_id)
	if chat.id != user.id:
		raise HTTPException(status_code=404, detail='Not Found.')

	session.delete(chat)
	session.commit()

	return {'msg': 'Chat successfully deleted!.', 'ok': True}


# if __name__ == '__main__':
# 	import uvicorn

# 	uvicorn.run(app=app, host='0.0.0.0')