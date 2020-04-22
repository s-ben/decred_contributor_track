from sqlalchemy import Column, Integer, String, DateTime, VARCHAR, ForeignKey
import datetime
from database import Base

# ----------- Create db models ---------------
class Event(Base):
    __tablename__ = "event_log"

    id = Column(Integer, primary_key=True)
    type_id = Column(Integer, ForeignKey('event_types.id'))
    repo_id = Column(Integer, ForeignKey('repository_list.id'))
    github_username = Column(String(49)) # 39 is max len of github username
    datetime = Column(DateTime, default=datetime.datetime.now)
    github_url = Column(VARCHAR(255),unique=True) #2083 max len of a URL, but cannot use 'unique' hope this is enough.
    sha = Column(String(40)) # commit sha hash
    merged_at = Column(DateTime)
    state = Column(String(10))

class Repo(Base):
    __tablename__ = "repository_list"

    id = Column(Integer, primary_key=True)
    name = Column(String(100),unique=True) #100 is max repo len
    organization = Column(String(39)) # 39 same as username.

class Event_type(Base):
    __tablename__ = "event_types"

    id = Column(Integer, primary_key=True)
    event_type = Column(String(128),unique=True)
