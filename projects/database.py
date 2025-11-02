from sqlmodel import SQLModel, Session, create_engine
import os


sqlite_url = os.getenv('SQLITE_URL', 'sqlite:///land_lend.db')
engine = create_engine(sqlite_url, echo=True)

#################################################################################################
# To use postgresql database: download postgres server and psql-cli and uncomment postgresql_url
# and engine.
# postgres url format: 'postgresql://<username>:<user-password>@<host>:<port>/database'
# start postgres server using: sudo systemctl start postgresql
# check status using: systemctl is-active postgresql
# create db using: psql -U postgres -c "create database land_lend_db;"
#################################################################################################

#postgresql_url = os.getenv('POSTGRESQL_URL', 'postgresql://postgres:postgres@127.0.0.1:5432/land_lend_db')
#engine = create_engine(postgresql_url, echo=True)

def init_db():
	SQLModel.metadata.create_all(engine)

def get_session():
	with Session(engine) as session:
		yield session
