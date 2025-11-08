# Bismillah

from fastapi import FastAPI

from .schemas.models import User, Land, Chat
from .database import init_db
from .routes import auth, users, lands, chats


app = FastAPI(
	prefix='/api/v1',
	description='Land Rent Management System.',
	#openapi_url=None
)

@app.on_event('startup')
async def startup():
	init_db()


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(lands.router)
app.include_router(chats.router)


@app.get('/')
async def index():
	return {'msg': 'Land Rent Management System'}