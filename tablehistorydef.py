from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

history_engine = create_engine('sqlite:///history.db', echo=True)
Base = declarative_base()


class Entry(Base):
	__tablename__ = "history"

	id = Column(Integer, primary_key=True)
	username = Column(String)
	number = Column(Integer)
	url = Column(String)

	def __init__(self, username, number, url):
		self.username = username
		self.number = number
		self.url = url


# create tables
Base.metadata.create_all(history_engine)
