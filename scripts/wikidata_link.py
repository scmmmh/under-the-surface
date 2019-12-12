import click
import json
import os
import re
import requests

from datetime import datetime

from models import Person
from util import merge_person_property, get_attribute


LINKED_ATTRIBUTES = (
    ('gender', 'claims.P21'),
    ('country_of_citizenship', 'claims.P27'),
    ('location_of_birth', 'claims.P19'),
    ('location_of_death', 'claims.P20'),
    ('languages_used', 'claims.P1412'),
    ('occupation', 'claims.P106'),
    ('residence', 'claims.P551'),
    ('field_of_work', 'claims.P101'),
    ('religion', 'claims.P140'),
    ('religious_order', 'claims.P611'),
    ('canonisation_status', 'claims.P411'),
)
TIME_ATTRIBUTES = (
    ('date_of_birth', 'claims.P569'),
    ('date_of_death', 'claims.P570'),
)
EXTERNAL_LINKS = (
    ('VIAF', 'https://viaf.org/viaf/{0}/', 'claims.P214'),
    ('GND', 'https://d-nb.info/gnd/{0}', 'claims.P227'),
)


@click.command()
@click.pass_context
def link_to_wikidata(ctx):
    """Link all people to Wikidata"""
    dbsession = ctx.obj['dbsession']
    for person in dbsession.query(Person):
        link_to_wikidata_person(dbsession, person)


QUERY_URL = 'https://www.wikidata.org/w/api.php?action=query&list=search&srsearch={0}&format=json'
DETAILS_URL = 'https://www.wikidata.org/wiki/Special:EntityData/{0}.json'


def link_to_wikidata_person(dbsession, person):
    """Link a single person to a Wikidata entry."""
    for result in query_wikidata(person.title):
        data = load_wikidata_attribute(result['title'], 'claims.P31')
        if data:
            source = {'url': QUERY_URL.format(person.title),
                      'label': 'Wikidata',
                      'timestamp': datetime.now()}
            for attr in data:
                if get_attribute(attr, 'mainsnak.datavalue.value.id') == 'Q5':
                    data = fetch_wikidata_page(result['title'])
                    matches = False
                    if person.title in [l['value'] for l in data['labels'].values()]:
                        matches = True
                    elif person.title in [l['value'] for a in data['aliases'].values() for l in a]:
                        matches = True
                    if matches:
                        merge_person_property(dbsession,
                                       person,
                                       'link',
                                       {'value': 'https://www.wikidata.org/wiki/{0}'.format(result['title']),
                                        'label': result['title']},
                                       source)
                        load_wikidata_data(dbsession, person, result['title'])
                    break


QUERY_CACHE = {}


def query_wikidata(query):
    """Query Wikidata for all pages matching the given query."""
    if query in QUERY_CACHE:
        return QUERY_CACHE[query]
    response = requests.get(QUERY_URL.format(query))
    if response.status_code == 200:
        data = response.json()
        if 'query' in data and 'search' in data['query']:
            QUERY_CACHE[query] = data['query']['search']
            return QUERY_CACHE[query]
    return []


def load_wikidata_attribute(title, attribute):
    """Load a single attribute from a Wikidata page."""
    data = fetch_wikidata_page(title)
    if data:
        return get_attribute(data, attribute.split('.'))


PAGE_CACHE = {}


def fetch_wikidata_page(title):
    """Fetch a page from Wikidata, caching the result."""
    global PAGE_CACHE
    if title in PAGE_CACHE:
        return PAGE_CACHE[title]
    response = requests.get(DETAILS_URL.format(title))
    if response.status_code == 200:
        data = response.json()
        if 'entities' in data and title in data['entities']:
            PAGE_CACHE[title] = data['entities'][title]
            return PAGE_CACHE[title]
    return None


def load_wikidata_data(dbsession, person, wikidata_id):
    """Load data from Wikidata."""
    source = {"url": DETAILS_URL.format(wikidata_id),
              "label": wikidata_id,
              'timestamp': datetime.now()}
    data = fetch_wikidata_page(wikidata_id)
    if data:
        for lang in ['en', 'de']:
            # Load labels and aliases
            if lang in data['labels']:
                merge_person_property(dbsession, person, 'name', {'value': data['labels'][lang]['value'], 'lang': lang}, source)
            if lang in data['aliases']:
                for label in data['aliases'][lang]:
                    merge_person_property(dbsession, person, 'name', {'value': label['value'], 'lang': lang}, source)
            # Load descriptions
            if lang in data['descriptions']:
                merge_person_property(dbsession, person, 'summary', {'value': data['descriptions'][lang]['value'], 'lang': lang}, source)
            # Load Wikipedia links
            if '{0}wiki'.format(lang) in data['sitelinks']:
                sitelinks = data['sitelinks']['{0}wiki'.format(lang)]
                merge_person_property(dbsession, person, 'link', {'value': sitelinks['url'], 'label': sitelinks['title'], 'lang':lang}, source)
            # Load other external links
            for label, key, path in EXTERNAL_LINKS:
                value = get_structured_attribute(data, path, None)
                if value:
                    for v in value:
                        merge_person_property(dbsession, person, 'link', {'value': key.format(v), 'label': label}, source)
            # Load linked attributes
            sub_path = 'labels.{0}.value'.format(lang)
            for key, path in LINKED_ATTRIBUTES:
                value = get_structured_attribute(data, path, sub_path)
                if value:
                    for v in value:
                        merge_person_property(dbsession, person, key, {'value': v, 'lang': lang}, source)
            # Load time attributes
            sub_path = 'time'
            for key, path in TIME_ATTRIBUTES:
                value = get_structured_attribute(data, path, sub_path)
                if value:
                    for v in value:
                        merge_person_property(dbsession, person, key, v, source)


def get_structured_attribute(data, path, sub_path):
    """Get a structured attribute, where necessary loading a linked Wikidata page."""
    attrs = get_attribute(data, path)
    result = []
    if attrs:
        for attr in attrs:
            if get_attribute(attr, 'mainsnak.datavalue.value.entity-type') == 'item':
                item = fetch_wikidata_page(get_attribute(attr, 'mainsnak.datavalue.value.id'))
                if item:
                    value = get_attribute(item, sub_path)
                    if value:
                        result.append(value)
            else:
                item = get_attribute(attr, 'mainsnak.datavalue.value')
                if item:
                    if sub_path:
                        value = get_attribute(item, sub_path)
                        if value:
                            result.append(value)
                    else:
                        result.append(item)
    if result:
        return result
    else:
        return None
