from sqlmodel import SQLModel, Field, Relationship
from pydantic import EmailStr
from datetime import datetime
from .enums import RoleEnum, IntendedUserEnum

################
## User
################

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

class UserOutWithLands(UserOut):
	lands: list['LandOut']


################
## Land
################

class LandBase(SQLModel):
	model_config = {'extra': 'forbid'}

	name: str = Field(index=True)
	address: str = Field(index=True)
	size: float | None = None
	location: str
	description: str | None = Field(default=None, index=True)

class Land(LandBase, table=True):
	id: int | None = Field(default=None, primary_key=True)
	lenders: list[User] = Relationship(back_populates='lands', link_model=UserLandLink)

	images: list['Image'] = Relationship(back_populates='land', cascade_delete=True)

class LandIn(LandBase):
	pass

class LandOut(LandBase):
	id: int
	images: list['ImageOut']

class LandUpdate(SQLModel):
	model_config = {'extra': 'forbid'}

	name: str | None = None
	address: str | None = None
	size: float | None = None
	location: str | None = None
	description: str | None = None

class LandOutWithUsers(LandOut):
	lenders: list[UserOut]


################
## Images
################

class ImageBase(SQLModel):
	model_config = {'extra': 'forbid'}

	label: str = Field(index=True)

class Image(ImageBase, table=True):
	id: int | None = Field(default=None, primary_key=True)
	url: str

	land_id: int = Field(foreign_key='land.id')
	land: Land = Relationship(back_populates='images')

class ImageIn(ImageBase):
	land_id: int | None = None

class ImageOut(ImageBase):
	id: int
	url: str

class ImagesUpdate(SQLModel):
	model_config = {'extra': 'forbid'}

	label: str | None = None
	

################
## Chat
################

class ChatBase(SQLModel):
	model_config = {'extra': 'forbid'}

	msg: str
	reciever_id: int | None = None
	intended_user: IntendedUserEnum

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
	intended_user: IntendedUserEnum | None = None
	reciever_id: int | None = None

#################
## Token
#################

class Token(SQLModel):
	access_token: str
	token_type: str