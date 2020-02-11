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

    properties = relationship('PersonProperty')
    display_properties = relationship('PersonProperty', primaryjoin="and_(Person.id == PersonProperty.person_id, PersonProperty.status.notin_(['incorrect', 'ignored']))")
    works = relationship('Work')
    display_works = relationship('Work', primaryjoin="and_(Person.id == Work.person_id, Work.status.notin_(['incorrect', 'ignored']))")


class PersonProperty(Base):

    __tablename__ = 'person_properties'

    id = Column(Integer(), primary_key=True)
    person_id = Column(Integer(), ForeignKey('people.id'))
    value_id = Column(Integer(), ForeignKey('values.id'))
    name = Column(String(255))
    status = Column(String(255))

    person = relationship('Person')
    value = relationship('Value')
    sources = relationship('PersonPropertySource')


class Work(Base):

    __tablename__ = 'works'

    id = Column(Integer(), primary_key=True)
    person_id = Column(Integer(), ForeignKey('people.id'))
    title = Column(String(255))
    status = Column(String(255))

    person = relationship('Person')
    sources = relationship('WorkSource')
    properties = relationship('WorkProperty')
    display_properties = relationship('WorkProperty', primaryjoin="and_(Work.id == WorkProperty.work_id, WorkProperty.status.notin_(['incorrect', 'ignored']))")


class WorkProperty(Base):

    __tablename__ = 'work_properties'
    id = Column(Integer(), primary_key=True)
    work_id = Column(Integer(), ForeignKey('works.id'))
    value_id = Column(Integer(), ForeignKey('values.id'))
    name = Column(String(255))
    status = Column(String(255))

    work = relationship('Work')
    value = relationship('Value')
    sources = relationship('WorkPropertySource')


class Value(Base):

    __tablename__ = 'values'

    id = Column(Integer(), primary_key=True)
    label = Column(String(255))
    value = Column(Text())
    lang = Column(String(255))


class PersonPropertySource(Base):

    __tablename__ = 'person_property_sources'

    property_id = Column(Integer(), ForeignKey('person_properties.id'), primary_key=True)
    source_id = Column(Integer(), ForeignKey('sources.id'), primary_key=True)
    timestamp = Column(DateTime())

    property = relationship('PersonProperty')
    source = relationship('Source')


class WorkSource(Base):

    __tablename__ = 'work_sources'

    work_id = Column(Integer(), ForeignKey('works.id'), primary_key=True)
    source_id = Column(Integer(), ForeignKey('sources.id'), primary_key=True)
    timestamp = Column(DateTime())

    work = relationship('Work')
    source = relationship('Source')


class WorkPropertySource(Base):

    __tablename__ = 'work_property_sources'

    property_id = Column(Integer(), ForeignKey('work_properties.id'), primary_key=True)
    source_id = Column(Integer(), ForeignKey('sources.id'), primary_key=True)
    timestamp = Column(DateTime())

    property = relationship('WorkProperty')
    source = relationship('Source')


class Source(Base):

    __tablename__ = 'sources'

    id = Column(Integer, primary_key=True)
    label = Column(String(255))
    url = Column(Text())
