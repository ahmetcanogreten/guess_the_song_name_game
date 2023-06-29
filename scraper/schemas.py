from sqlalchemy import (
    create_engine,
    Column,
    Integer,
    Text,
    ForeignKey,
)
from sqlalchemy.engine import URL
from sqlalchemy.orm import declarative_base
from datetime import datetime


url = URL.create(
    drivername="postgresql",
    host="localhost",
    port=5432,
    username="postgres",
    password="postgres",
    database="postgres",
)

engine = create_engine(url)

connection = engine.connect()

Base = declarative_base()


class Artist(Base):
    __tablename__ = "artists"

    id = Column(Integer(), primary_key=True)
    name = Column(Text, nullable=False)


class Song(Base):
    __tablename__ = "songs"

    id = Column(Integer(), primary_key=True)
    artist_id = Column(Integer(), ForeignKey("artists.id"))
    name = Column(Text, nullable=False)
    lyrics = Column(Text, nullable=False)


Base.metadata.create_all(engine)
