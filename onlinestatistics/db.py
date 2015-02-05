#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Create on:2015.1.3
#Version:0.0.1

"""
数据库o_o
"""

from sqlalchemy import Column, create_engine,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgres import JSONB, INTEGER
from sqlalchemy.orm import sessionmaker
from datetime import datetime


Base = declarative_base()


class Online(Base):
    __tablename__ = "Online"
    _time = Column(DateTime, primary_key=True)
    status_code = Column(INTEGER)
    content = Column(JSONB)
    online = Column(INTEGER)


engine = create_engine('postgresql+psycopg2://{user}:{pwd}@{host}:{port}/{database}'.format(database='test',
                                                                                            user='test_postgres',
                                                                                            pwd='123456',
                                                                                            host='localhost',
                                                                                            port='5432'))
Base.metadata.create_all(engine)
session = sessionmaker()
session.configure(bind=engine)
s = session()

def insert(content,status_code,online):
    o = Online(_time=datetime.utcnow(),status_code=int(status_code),content=content,online=int(online))
    s.add(o)
    s.commit()

