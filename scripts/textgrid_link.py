import click
import json
import os
import re
import requests

from datetime import datetime
from lxml import etree

from models import Person
from util import merge_work, merge_work_property, get_attribute, get_xml_attribute


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
@click.pass_context
def load_textgrid_data(ctx):
    dbsession = ctx.obj['dbsession']
    with click.progressbar(dbsession.query(Person), length=dbsession.query(Person).count(), label='Linking People') as bar:
        for person in bar:
            data = fetch_textgrid_search(person.title)
            if data:
                source = {'url': QUERY_URL.format(person.title),
                          'label': 'TextGrid API',
                          'timestamp': datetime.now()}
                data = etree.fromstring(data)
                if int(data.attrib['hits']) > 0:
                    for result in data:
                        agent = get_xml_attribute(result, 'tg:object.tg:edition.tg:agent', ns=NAMESPACES)
                        if agent is not None and agent.text == format_query_author(person.title) and 'role' in agent.attrib and agent.attrib['role'] == 'author':
                            title = get_xml_attribute(result,
                                                      'tg:object.tg:generic.tg:provided.tg:title.text()',
                                                      ns=NAMESPACES)
                            tgid = get_xml_attribute(result,
                                                     'tg:object.tg:generic.tg:generated.tg:textgridUri.text()',
                                                     ns=NAMESPACES)
                            work = merge_work(dbsession, person, title, source)
                            merge_work_property(dbsession, work, '{0}§provider'.format(tgid), {'label': 'TextGrid', 'value': 'https://textgridrep.org'}, source)
                            merge_work_property(dbsession, work, '{0}§data'.format(tgid), {'value': ITEM_URL.format(tgid)}, source)
                            merge_work_property(dbsession, work, '{0}§license'.format(tgid), {'label': 'CC-BY', 'value': 'cc-by'}, source)
                            merge_work_property(dbsession, work, '{0}§license_url'.format(tgid), {'value': 'https://textgrid.de/Digitale-Bibliothek'}, source)
