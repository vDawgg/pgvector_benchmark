from sqlalchemy import Integer, String, Column
from sqlalchemy.orm import mapped_column
from pgvector.sqlalchemy import Vector
from db.db import Base, engine

# TODO: Think about setting this some other way
dim = 768


class Item(Base):
    __tablename__ = "vecdatatable"
    id = Column(Integer, primary_key=True, autoincrement=True)
    q_id = Column(Integer, nullable=False)
    text = Column(String, nullable=False)
    vec = mapped_column(Vector(dim), nullable=False)


Base.metadata.create_all(bind=engine)
