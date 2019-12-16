import click
import requests
import json

from datetime import datetime
from lxml import etree
from sqlalchemy import and_

from models import Person, PersonProperty, Value
from util import merge_person_property, merge_work, slugify


@click.command()
@click.argument('names', nargs=-1)
@click.pass_context
def add_people_via_viaf(ctx, names):
    """Add new people linked to VIAF"""
    dbsession = ctx.obj['dbsession']
    for name in names:
        link_new_person(dbsession, name)


@click.command()
@click.pass_context
def link_to_viaf(ctx):
    """Link to people and works in the VIAF"""
    dbsession = ctx.obj['dbsession']
    for person in dbsession.query(Person):
        has_viaf = False
        for property in person.display_properties:
            if property.name == 'viafid':
                link_data(dbsession, person, property.value.value)


QUERY_URL = 'http://viaf.org/viaf/AutoSuggest?query={0}'
MENU_ENTRY = '{0}: {1} (https://viaf.org/viaf/{2})'


def link_new_person(dbsession, name):
    """Link an individual to VIAF, requiring confirmation from the user."""
    response = requests.get(QUERY_URL.format(name))
    if response.status_code == 200:
        data = response.json()
        if data['result']:
            records = list(enumerate([record for record in data['result'] if record['nametype'] == 'personal']))
            if records:
                source = {'url': QUERY_URL.format(name),
                          'label': 'VIAF Autosuggest Query',
                          'timestamp': datetime.now()}
                print('Available records for {0}'.format(name))
                for idx, record in records:
                    print(MENU_ENTRY.format(idx + 1, record['displayForm'], record['viafid']))
                print('0: None of the above')
                selected = -1
                while selected < 0 or selected > len(records):
                    selected = click.prompt('Which record to link', type=int)
                if selected > 0:
                    selected = selected - 1
                    exists = dbsession.query(PersonProperty).join(Value).filter(and_(PersonProperty.name == 'viafid',
                                                                                     Value.value == records[selected][1]['viafid'])).first()
                    if not exists:
                        person = Person(title=name,
                                        slug=slugify(name),
                                        status='unconfirmed')
                        dbsession.add(person)
                        dbsession.commit()
                        db_property = merge_person_property(dbsession, person, 'viafid', records[selected][1]['viafid'], source)
                        db_property.status = 'confirmed'
                        dbsession.add(db_property)
                        dbsession.commit()


DETAILS_URL = 'https://viaf.org/viaf/{0}/viaf.xml'
NS = {'viaf': 'http://viaf.org/viaf/terms#'}


def link_data(dbsession, person, viafid):
    """Link the person to the data identified by the viafid."""
    response = requests.get(DETAILS_URL.format(viafid))
    if response.status_code == 200:
        source = {'url': DETAILS_URL.format(viafid),
                  'label': 'VIAF Record',
                  'timestamp': datetime.now()}
        doc = etree.fromstring(response.content)
        for source_id in doc.xpath('/viaf:VIAFCluster//viaf:sources/viaf:source/text()', namespaces=NS):
            if source_id.startswith('DNB|'):
                merge_person_property(dbsession, person, 'gndid', source_id[4:], source)
            if source_id.startswith('WKP|'):
                merge_person_property(dbsession, person, 'wikidataid', source_id[4:], source)
        for work in doc.xpath('/viaf:VIAFCluster/viaf:titles/viaf:work/viaf:title/text()', namespaces=NS):
            merge_work(dbsession, person, work, source)
