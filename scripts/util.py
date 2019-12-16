from datetime import datetime
from sqlalchemy import and_

from models import Person, PersonProperty, Work, WorkProperty, Value, Source, PersonPropertySource, WorkSource, WorkPropertySource


def get_attribute(obj, path, default=None):
    """Get the value in obj at path."""
    if isinstance(path, str):
        path = path.split('.')
    if path:
        if path[0] in obj:
            if len(path) == 1:
                return obj[path[0]]
            else:
                return get_attribute(obj[path[0]], path[1:], default=default)
    return default


def get_xml_attribute(obj, path, default=None, ns=None):
    if isinstance(path, str):
        path = path.split('.')
    if path:
        if path[0].startswith('@'):
            if path[0][1:] in obj.attrib:
                return obj.attrib[path[0][1:]]
        elif path[0] == 'text()':
            return obj.text
        else:
            for child in obj:
                if ns:
                    tag = '{ns}:{tag}'.format(ns=ns[child.tag[:child.tag.find('}') + 1]],
                                              tag=child.tag[child.tag.find('}') + 1:])
                else:
                    tag = child.tag
                if tag == path[0]:
                    if len(path) == 1:
                        return child
                    else:
                        return get_xml_attribute(child, path[1:], default=default, ns=ns)
    return default


def json_utcnow():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')


def merge_person_property(dbsession, person, property, value, source):
    """Merge the given ``property`` with ``value`` into the ``person``. Attribute the change to the ``source``.
    ``value`` can be a string or a dictionary with keys "label", "lang", and "value". ``source`` is a dictionary
    with keys "label", "source", and "timestamp".
    """
    if isinstance(value, dict):
        label = value['label'] if 'label' in value else None
        lang = value['lang'] if 'lang' in value else None
        value = value['value']
    else:
        label = None
        lang = None
    db_property = dbsession.query(PersonProperty).join(Value).filter(and_(PersonProperty.person_id == person.id,
                                                                          PersonProperty.name == property,
                                                                          Value.value == value,
                                                                          Value.lang == lang)).first()
    if not db_property:
        db_value = dbsession.query(Value).filter(and_(Value.value == value,
                                                      Value.lang == lang)).first()
        if not db_value:
            db_value = Value(label=label, value=value, lang=lang)
            dbsession.add(db_value)
        db_property = PersonProperty(person=person, name=property, value=db_value, status='unconfirmed')
        dbsession.add(db_property)
    property_source = dbsession.query(PersonPropertySource).join(Source).filter(and_(PersonPropertySource.property == db_property,
                                                                                     Source.url == source['url'])).first()
    if not property_source:
        db_source = dbsession.query(Source).filter(Source.url == source['url']).first()
        if not db_source:
            db_source = Source(label=source['label'], url=source['url'])
            dbsession.add(db_source)
        property_source = PersonPropertySource(property=db_property, source=db_source, timestamp=source['timestamp'])
        dbsession.add(property_source)
    else:
        property_source.timestamp = source['timestamp']
        dbsession.add(property_source)
    dbsession.commit()
    return db_property


def merge_work(dbsession, person, title, source):
    work = dbsession.query(Work).filter(and_(Work.person_id == person.id, Work.title == title)).first()
    if not work:
        work = Work(person=person, title=title, status='unconfirmed')
        dbsession.add(work)
        dbsession.commit()
    else:
        work_source = dbsession.query(WorkSource).join(Source).filter(and_(WorkSource.work == work,
                                                                           Source.url == source['url'])).first()
        if not work_source:
            db_source = dbsession.query(Source).filter(Source.url == source['url']).first()
            if not db_source:
                db_source = Source(label=source['label'], url=source['url'])
                dbsession.add(db_source)
            work_source = WorkSource(work=work, source=db_source, timestamp=source['timestamp'])
            dbsession.add(work_source)
        else:
            work_source.timestamp = source['timestamp']
            dbsession.add(work_source)
        dbsession.commit()
    return work


def merge_work_property(dbsession, work, property, value, source):
    """Merge the given ``property`` with ``value`` into the ``work``. Attribute the change to the ``source``.
    ``value`` can be a string or a dictionary with keys "label", "lang", and "value". ``source`` is a dictionary
    with keys "label", "source", and "timestamp".
    """
    if isinstance(value, dict):
        label = value['label'] if 'label' in value else None
        lang = value['lang'] if 'lang' in value else None
        value = value['value']
    else:
        label = None
        lang = None
    db_property = dbsession.query(WorkProperty).join(Value).filter(and_(WorkProperty.work_id == work.id,
                                                                        WorkProperty.name == property,
                                                                        Value.value == value,
                                                                        Value.lang == lang)).first()
    if not db_property:
        db_value = dbsession.query(Value).filter(and_(Value.value == value,
                                                      Value.lang == lang)).first()
        if not db_value:
            db_value = Value(label=label, value=value, lang=lang)
            dbsession.add(db_value)
        db_property = WorkProperty(work=work, name=property, value=db_value, status='unconfirmed')
        dbsession.add(db_property)
    property_source = dbsession.query(WorkPropertySource).join(Source).filter(and_(WorkPropertySource.property == db_property,
                                                                                   Source.url == source['url'])).first()
    if not property_source:
        db_source = dbsession.query(Source).filter(Source.url == source['url']).first()
        if not db_source:
            db_source = Source(label=source['label'], url=source['url'])
            dbsession.add(db_source)
        property_source = WorkPropertySource(property=db_property, source=db_source, timestamp=source['timestamp'])
        dbsession.add(property_source)
    else:
        property_source.timestamp = source['timestamp']
        dbsession.add(property_source)
    dbsession.commit()
