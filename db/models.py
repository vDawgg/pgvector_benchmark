from db.db import Base
from sqlalchemy import Integer, String, Column, Engine
from sqlalchemy.orm import mapped_column
from pgvector.sqlalchemy import Vector
import numpy as np

dim = 768


class Item(Base):
    __tablename__ = "vecdatatable"
    id = Column(Integer, primary_key=True, autoincrement=True)
    q_id = Column(Integer, nullable=False)
    vec = mapped_column(Vector(dim), nullable=False)


def init_mappings(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


def item_to_qid_array(items):
    return np.array([item.q_id for item in items])
