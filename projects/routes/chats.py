from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, Session, or_
from ..schemas.models import User, Chat, ChatIn, ChatOut, ChatUpdate
from ..schemas.enums import RoleEnum, IntendedUserEnum
from ..database import get_session
from ..utils.security import (
			get_current_active_user,
			authorize_user
)


router = APIRouter(
    prefix='/chats'
)


@router.post(
	'/', 
	status_code=201
)
async def register_chat(*,
	chat: ChatIn,
	reciever_id: int | None = None,
	user: Annotated[
		User, 
		Depends(authorize_user(
				[RoleEnum.normal_user,
				RoleEnum.security,
				RoleEnum.staff]))],
	session: Annotated[Session, Depends(get_session)]
):
	new_chat = Chat.model_validate(chat)

	new_chat.sender_id = user.id

	if chat.intended_user == 'ALL' and reciever_id is not None:
		raise HTTPException(status_code=400, detail='You can send request with both reciever_id and intented_user="ALL".')

	if chat.intended_user == 'ONE':
		if not reciever_id:
			raise HTTPException(status_code=400, detail='reciever_id is not set.')
		
		reciever = session.get(User, reciever_id)
		if not reciever:
			raise HTTPException(status_code=404, detail=f'User with id={reciever_id} you intended to send message to doesn\'t exists')

		new_chat.reciever_id = reciever.id
	
	session.add(new_chat)
	session.commit()

@router.get(
	'/',
	response_model=list[ChatOut]
)
async def fetch_chats(*,
	user: Annotated[User, Depends(get_current_active_user)],
	skip: int = 0, limit: int = 100,
	session: Annotated[Session, Depends(get_session)]
):
	chats = session.exec(
		select(Chat).where(or_(Chat.reciever_id == user.id, Chat.intended_user == IntendedUserEnum.ALL)).offset(skip).limit(limit)
	).all()

	if not chats:
		raise HTTPException(status_code=404, detail='No Chats yet!.')

	return chats

@router.patch(
	'/{chat_id}',
	response_model=ChatOut
)
async def update_chat(
	chat_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
	update_data: ChatUpdate,
	session: Annotated[Session, Depends(get_session)]
):
	chat = session.get(Chat, chat_id)
	if not chat:
		raise HTTPException(status_code=400, detail=f'Chat with id={user.id} not found.')
	
	if chat.reciever_id is None and update_data.intended_user == IntendedUserEnum.ONE:
		raise HTTPException(status_code=400, detail='Reciever id must be set.')

	if chat.sender_id != user.id:
		raise HTTPException(status_code=405, detail='Not authorize.')

	if not chat:
		raise HTTPException(status_code=404, detail='Chat not Found.')
	
	update_data = Chat.model_dump(update_data, exclude_unset=True)

	chat.sqlmodel_update(update_data)

	session.add(chat)
	session.commit()
	
	session.refresh(chat)

	return chat


@router.delete('/{chat_id}')
async def delete_chat(
	chat_id: int,
	user: Annotated[User, Depends(get_current_active_user)],
	session: Annotated[Session, Depends(get_session)]
):
	chat = session.get(Chat, chat_id)
	if not chat:
		raise HTTPException(status_code=404, detail='Chat not found.')

	if chat.sender_id != user.id:
		raise HTTPException(status_code=404, detail='Not Found.')

	session.delete(chat)
	session.commit()

	return {'msg': 'Chat successfully deleted!.', 'ok': True}