import datetime
from peewee import *
db = SqliteDatabase('fifpro.db')

class BaseModel(Model):

	class Meta:
		database = db

class User(BaseModel):
	username = CharField(unique=True)
	password = CharField()
	matches_played = IntegerField(default=0)
	is_moderater = BooleanField(default=False)
	join_date = DateTimeField(default=datetime.datetime.now)


def init_db():
	db.connect()
	db.create_tables([User], safe=True)