from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime
from .enums import RoleEnum


class UserLandLink(SQLModel, table=True):
	user_id: int | None = Field(default=None, primary_key=True, foreign_key='user.id')
	land_id: int | None = Field(default=None, primary_key=True, foreign_key='land.id')

class UserBase(SQLModel):
	model_config = {'extra': 'forbid'}
	username: str = Field(index=True)
	full_name: str = Field(index=True)
	email: EmailStr = Field(index=True)
	address: str
	phone_number: str
	

class User(UserBase, table=True):
	id: int | None = Field(default=None, primary_key=True)
	hashed_password: str
	role: RoleEnum | None = 'normal_user'
	disabled: bool = False
	lands: list['Land'] = Relationship(back_populates='lenders', link_model=UserLandLink)

class UserIn(UserBase):
	password: str = Field(min_length=6)

class UserOut(UserBase):
	id: int
	role: RoleEnum | None = 'normal_user'
	disabled: bool

class UserUpdate(SQLModel):
	model_config = {'extra': 'forbid'}
	username: str | None = None
	email: EmailStr | None = None
	address: str | None = None
	phone_number: str | None = None
	password: str | None = None

class UserAdminUpdate(SQLModel):
	model_config = {'extra': 'forbid'}
	disabled: bool | None = None
	role: RoleEnum | None = None
	disabled: bool

################
## Land
################

# helper nest class Image.
# class Image(SQLModel):
# 	name: str
# 	url: HttpUrl

class LandBase(SQLModel):
	model_config = {'extra': 'forbid'}
	name: str = Field(index=True)
	address: str = Field(index=True)
	size: float | None = None
	location: str
	description: str | None = Field(default=None, index=True)
	url: str


class Land(LandBase, table=True):
	id: int | None = Field(default=None, primary_key=True)
	lenders: list[User] = Relationship(back_populates='lands', link_model=UserLandLink)

class LandIn(LandBase):
	pass

class LandOut(LandBase):
	id: int

class LandUpdate(SQLModel):
	model_config = {'extra': 'forbid'}
	name: str | None = None
	address: str | None = None
	size: float | None = None
	location: str | None = None
	description: str | None = None
	url: str | None = None

################
## Chat
################

class ChatBase(SQLModel):
	model_config = {'extra': 'forbid'}
	msg: str
	receiver_id: int | None = Field(default=None, foreign_key='user.id')
	intended_user: RoleEnum | None = None

	sender_id: int | None = Field(default=None, foreign_key='user.id')

class Chat(ChatBase, table=True):
	id: int | None = Field(default=None, primary_key=True)
	sent_at: datetime = Field(default_factory=datetime.now)

class ChatIn(ChatBase):
	pass

class ChatOut(ChatBase):
	id: int
	sent_at: datetime

class ChatUpdate(SQLModel):
	model_config = {'extra': 'forbid'}
	msg: str | None = None
	intended_user: RoleEnum | None = None