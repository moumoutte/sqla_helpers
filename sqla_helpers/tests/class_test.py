# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

from sqla_helpers.base_model import BaseModel

DeclarativeModel = declarative_base(cls=BaseModel)
metadata = DeclarativeModel.metadata

class Treatment(DeclarativeModel):
    __tablename__ = 'treatment'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)
    status_id = Column('status_id', ForeignKey("status.id"))
    status = relationship('Status', backref='treatments')


class Status(DeclarativeModel):
    __tablename__ = 'status'
    id = Column('id', Integer, primary_key=True)
    name = Column('name', String)

    def __init__(self, name):
	self.name = name
