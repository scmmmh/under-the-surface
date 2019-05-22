import click
import json
import os
import re
import requests

from datetime import datetime
from lxml import etree

from util import get_attribute, get_xml_attribute, add_to_set, json_utcnow


QUERY_URL = 'https://textgridlab.org/1.0/tgsearch-public/search?q=edition.agent.value:"{0}"&limit=100'
NAMESPACES = {
    '{http://textgrid.info/namespaces/metadata/core/2010}': 'tg',
    '{http://www.textgrid.info/namespaces/middleware/tgsearch}': 'tgs'
}
SEARCH_CACHE = {}
NAME_STRUCTURE = '{givenName}, {firstName}'
ITEM_URL = 'https://textgridlab.org/1.0/aggregator/teicorpus/{0}?flat=true'


def format_query_author(title):
    if ' von ' in title:
        return NAME_STRUCTURE.format(givenName=title[title.find(' von ') + 5:].strip(),
                                     firstName=title[:title.find(' von ') + 5].strip())
    title = title.split()
    return NAME_STRUCTURE.format(givenName=title[-1],
                                 firstName=' '.join(title[:-1]))


def fetch_textgrid_search(title):
    global SEARCH_CACHE
    if title not in SEARCH_CACHE:
        response = requests.get(QUERY_URL.format(format_query_author(title)))
        if response.status_code == 200:
            SEARCH_CACHE[title] = response.content
    if title in SEARCH_CACHE:
        return SEARCH_CACHE[title]
    else:
        return None


@click.command()
def load_textgrid_data():
    for basepath, _, files in os.walk(os.path.join('content', 'people')):
        for filename in files:
            if re.match('.+\.[a-z]{2}\.json', filename):
                with open(os.path.join(basepath, filename)) as in_f:
                    obj = json.load(in_f)
                person_title = get_attribute(obj, 'data.attributes.title')
                data = fetch_textgrid_search(person_title)
                source = {'source': QUERY_URL.format(person_title),
                          'timestamp': json_utcnow()}
                if data:
                    data = etree.fromstring(data)
                    if int(data.attrib['hits']) > 0:
                        found = False
                        for result in data:
                            agent = get_xml_attribute(result, 'tg:object.tg:edition.tg:agent', ns=NAMESPACES)
                            if agent is not None and agent.text == format_query_author(person_title) and 'role' in agent.attrib and agent.attrib['role'] == 'author':
                                found = True
                                title = get_xml_attribute(result,
                                                          'tg:object.tg:generic.tg:provided.tg:title.text()',
                                                          ns=NAMESPACES)
                                tgid = get_xml_attribute(result,
                                                         'tg:object.tg:generic.tg:generated.tg:textgridUri.text()',
                                                         ns=NAMESPACES)
                                add_to_set(obj,
                                           'data.attributes.works',
                                           {'title': title,
                                            'url': ITEM_URL.format(tgid),
                                            'provider': {
                                                'title': 'TextGrid Repository',
                                                'url': 'https://textgridrep.org'
                                           },
                                           'license': {'type': 'cc-by',
                                                       'url': 'https://textgrid.de/Digitale-Bibliothek'}},
                                           source)
                        if found:
                            add_to_set(obj, 'data.attributes.sources', 'TextGrid Repository', source)
                with open(os.path.join(basepath, filename), 'w') as out_f:
                    json.dump(obj, out_f, indent=4)
