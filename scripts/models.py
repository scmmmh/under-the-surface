from sqlalchemy import Table, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship


Base = declarative_base()

class Person(Base):

    __tablename__ = 'people'

    id = Column(Integer(), primary_key=True)
    slug = Column(String(255), unique=True)
    title = Column(Text())
    status = Column(String(255))

    properties = relationship('Property')
    display_properties = relationship('Property', primaryjoin="and_(Person.id == Property.person_id, Property.status != 'incorrect')")


class Property(Base):

    __tablename__ = 'properties'

    id = Column(Integer(), primary_key=True)
    person_id = Column(Integer(), ForeignKey('people.id'))
    value_id = Column(Integer(), ForeignKey('values.id'))
    name = Column(String(255))
    status = Column(String(255))

    person = relationship('Person')
    value = relationship('Value')
    sources = relationship('SourceTimestamp')


class Value(Base):

    __tablename__ = 'values'

    id = Column(Integer(), primary_key=True)
    label = Column(String(255))
    value = Column(Text())
    lang = Column(String(255))


class SourceTimestamp(Base):

    __tablename__ = 'source_timestamps'

    property_id = Column(Integer(), ForeignKey('properties.id'), primary_key=True)
    source_id = Column(Integer(), ForeignKey('sources.id'), primary_key=True)
    timestamp = Column(DateTime())

    property = relationship('Property')
    source = relationship('Source')


class Source(Base):

    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    label = Column(String(255))
    url = Column(Text())
