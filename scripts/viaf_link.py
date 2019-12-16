import click
import requests
import json

from datetime import datetime

from models import Person
from util import merge_person_property


@click.command()
@click.option('--no-user', default=False, is_flag=True)
@click.pass_context
def link_to_viaf(ctx, no_user):
    """Link to people and works in the VIAF"""
    dbsession = ctx.obj['dbsession']
    for person in dbsession.query(Person):
        has_viaf = False
        for property in person.display_properties:
            if property.name == 'viafid':
                has_viaf = True
        if has_viaf:
            pass
        elif not no_user:
            link_person(dbsession, person)


QUERY_URL = 'http://viaf.org/viaf/AutoSuggest?query={0}'
MENU_ENTRY = '{0}: {1} (https://viaf.org/viaf/{2})'


def link_person(dbsession, person):
    """Link an individual to VIAF, requiring confirmation from the user."""
    response = requests.get(QUERY_URL.format(person.title))
    if response.status_code == 200:
        data = response.json()
        if data['result']:
            records = list(enumerate([record for record in data['result'] if record['nametype'] == 'personal']))
            if records:
                source = {'url': QUERY_URL.format(person.title),
                          'label': 'VIAF Autosuggest Query',
                          'timestamp': datetime.now()}
                print('Available records for {0}'.format(person.title))
                for idx, record in records:
                    print(MENU_ENTRY.format(idx + 1, record['displayForm'], record['viafid']))
                print('0: None of the above')
                selected = -1
                while selected < 0 or selected > len(records):
                    selected = click.prompt('Which record to link', type=int)
                if selected > 0:
                    selected = selected - 1
                    db_property = merge_person_property(dbsession, person, 'viafid', records[selected][1]['viafid'], source)
                    db_property.status = 'confirmed'
                    dbsession.add(db_property)
                    dbsession.commit()
