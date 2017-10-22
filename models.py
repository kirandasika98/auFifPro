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


class Match(BaseModel):
	player1 = ForeignKeyField(User, related_name='player1')
	player2 = ForeignKeyField(User, related_name='player2')
	player1_goals = IntegerField(default=0)
	player2_goals = IntegerField(default=0)
	pub_date = DateTimeField(default=datetime.datetime.now)


def init_db():
	db.create_tables([User, Match], safe=True)