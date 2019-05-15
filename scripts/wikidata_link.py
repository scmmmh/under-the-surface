import click
import json
import os
import re
import requests

from datetime import datetime


LINKED_ATTRIBUTES = (
    ('data.attributes.gender', 'claims.P21'),
    ('data.attributes.country_of_citizenship', 'claims.P27'),
    ('data.attributes.location_of_birth', 'claims.P19'),
    ('data.attributes.location_of_death', 'claims.P20'),
    ('data.attributes.languages_used', 'claims.P1412'),
    ('data.attributes.occupation', 'claims.P106'),
    ('data.attributes.residence', 'claims.P551'),
    ('data.attributes.field_of_work', 'claims.P101'),
    ('data.attributes.religion', 'claims.P140'),
    ('data.attributes.religious_order', 'claims.P611'),
    ('data.attributes.canonisation_status', 'claims.P411'),
)
TIME_ATTRIBUTES = (
    ('data.attributes.date_of_birth', 'claims.P569'),
    ('data.attributes.date_of_death', 'claims.P570'),
)
EXTERNAL_LINKS = (
    ('data.attributes.links.viaf', 'claims.P214'),
    ('data.attributes.links.gnd', 'claims.P227'),
)


@click.command()
def link_to_wikidata():
    """Link all people to Wikidata"""
    for basepath, _, files in os.walk(os.path.join('content', 'people')):
        for filename in files:
            if re.match('.+\.[a-z]{2}\.json', filename):
                with open(os.path.join(basepath, filename)) as in_f:
                    obj = json.load(in_f)
                if 'links' not in obj['data']['attributes'] or 'wikidata' not in obj['data']['attributes']['links']:
                    obj = link_to_wikidata_person(obj)
                    with open(os.path.join(basepath, filename), 'w') as out_f:
                        json.dump(obj, out_f, indent=2)


QUERY_URL = 'https://www.wikidata.org/w/api.php?action=query&list=search&srsearch={0}&format=json'
DETAILS_URL = 'https://www.wikidata.org/wiki/Special:EntityData/{0}.json'


def link_to_wikidata_person(obj):
    """Link a single person to a Wikidata entry."""
    for result in query_wikidata(obj['data']['attributes']['title']):
        data = load_wikidata_attribute(result['title'], 'claims.P31')
        if data:
            for attr in data:
                # Check that the Wikidata record is a person
                if get_attribute(attr, 'mainsnak.datavalue.value.id') == 'Q5':
                    set_value(obj,
                              'data.attributes.links.wikidata.{0}'.format(result['title']),
                              None)
    return obj


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


def get_attribute(obj, path, default=None):
    """Get the value in obj at path."""
    if isinstance(path, str):
        path = path.split('.')
    if path:
        if path[0] in obj:
            if len(path) == 1:
                return obj[path[0]]
            else:
                return get_attribute(obj[path[0]], path[1:])
    return default


def set_value(obj, path, value):
    """Set the value at path in obj."""
    if isinstance(path, str):
        path = path.split('.')
    tmp = obj
    for component in path[:-1]:
        if component not in tmp:
            tmp[component] = {}
        tmp = tmp[component]
    if path[-1] not in tmp:
        tmp[path[-1]] = {}
    tmp[path[-1]] = value


def add_to_set(obj, path, value):
    """Add a value to the set at location path in obj."""
    if isinstance(path, str):
        path = path.split('.')
    tmp = obj
    for component in path[:-1]:
        if component not in tmp:
            tmp[component] = {}
        tmp = tmp[component]
    if path[-1] not in tmp:
        tmp[path[-1]] = []
    elif not isinstance(tmp[path[-1]], list):
        tmp[path[-1]] = [tmp[path[-1]]]
    if value not in tmp[path[-1]]:
        tmp[path[-1]].append(value)


@click.command()
def load_wikidata_data():
    """Load data from Wikidata."""
    for basepath, _, files in os.walk(os.path.join('content', 'people')):
        for filename in files:
            if re.match('.+\.[a-z]{2}\.json', filename):
                with open(os.path.join(basepath, filename)) as in_f:
                    obj = json.load(in_f)
                lang = get_attribute(obj, 'data.attributes.lang')
                for source_key, value in list(get_attribute(obj, 'data.attributes.links.wikidata').items()):
                    if value is None:
                        data = fetch_wikidata_page(source_key)
                        if data:
                            # Load main label
                            if lang in data['labels']:
                                add_to_set(obj, 'data.attributes.names', data['labels'][lang]['value'])
                            # Load alternative labels
                            if lang in data['aliases']:
                                for label in data['aliases'][lang]:
                                    add_to_set(obj, 'data.attributes.names', label['value'])
                            # Load content summary
                            if lang in data['descriptions']:
                                add_to_set(obj, 'data.attributes.content', data['descriptions'][lang]['value'])
                            # Load links to Wikipedia
                            if '{0}wiki'.format(lang) in data['sitelinks']:
                                sitelinks = data['sitelinks']['{0}wiki'.format(lang)]
                                set_value(obj,
                                          'data.attributes.links.wikipedia.site',
                                          {'label': sitelinks['title'], 'url': sitelinks['url']})
                            # Load other external links
                            for key, path in EXTERNAL_LINKS:
                                value = get_structured_attribute(data, path, None)
                                if value:
                                    for v in value:
                                        set_value(obj,
                                                  '{0}.{1}'.format(key, v),
                                                  {'url': 'https://viaf.org/viaf/{0}/'.format(v)})
                            # Load linked attributes
                            sub_path = 'labels.{0}.value'.format(lang)
                            for key, path in LINKED_ATTRIBUTES:
                                value = get_structured_attribute(data, path, sub_path)
                                if value:
                                    for v in value:
                                        add_to_set(obj, key, v)
                            # Load time attributes
                            sub_path = 'time'
                            for key, path in TIME_ATTRIBUTES:
                                value = get_structured_attribute(data, path, sub_path)
                                if value:
                                    for v in value:
                                        add_to_set(obj, key, v)
                            # Set loading timestamp
                            set_value(obj,
                                      'data.attributes.links.wikidata.{0}'.format(source_key),
                                      {'timestamp': datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                                       'url': 'https://www.wikidata.org/wiki/{0}'.format(source_key)})
                            # Set the verification level
                            if get_attribute(obj, 'data.attributes.verification') in ['partial', 'full']:
                                set_value(obj,
                                          'data.attributes.verification',
                                          'partial')
                            else:
                                set_value(obj,
                                          'data.attributes.verification',
                                          'none')
                with open(os.path.join(basepath, filename), 'w') as out_f:
                    json.dump(obj, out_f, indent=2)


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
