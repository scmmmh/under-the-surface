import click
import re
import requests

from datetime import datetime
from lxml import etree
from sqlalchemy import and_

from models import Person
from util import merge_work, merge_work_property


@click.command()
@click.pass_context
def link_to_dta(ctx):
    """Link to works in the DTA"""
    dbsession = ctx.obj['dbsession']
    with click.progressbar(dbsession.query(Person), length=dbsession.query(Person).count(), label='Linking People') as bar:
        for person in bar:
            for db_property in person.properties:
                if db_property.name == 'gndid':
                    link_person(dbsession, person, db_property.value.value)


def link_person(dbsession, person, gnd):
    """Link all of a person's works identified via the ``gnd``."""
    response = requests.post('http://www.deutschestextarchiv.de/search/metadata', data={'select-1': 'pnd', 'search-1': gnd, 'search': '1'})
    if response.status_code == 200:
        match = re.search('Es wurden ([0-9]+) Werke? gefunden', response.text)
        if match:
            if int(match.group(1)) > 0:
                source = {'url': 'http://www.deutschestextarchiv.de/search/metadata?select-1=pnd&search-1={0}&search=1'.format(gnd),
                          'label': 'Deutsches Textarchiv',
                          'timestamp': datetime.now()}
                doc = etree.fromstring(response.text, etree.HTMLParser())
                for link in doc.xpath("//div[@id='meta-results-short']//a"):
                    link_work(dbsession, person, link.attrib['href'][link.attrib['href'].rfind('/') + 1:], source)


WORK_TEI_HEADER_URL = 'http://www.deutschestextarchiv.de/api/tei_header/{0}'
WORK_HTML_URL = 'http://www.deutschestextarchiv.de/book/show/{0}'
WORK_TEI_URL = 'http://www.deutschestextarchiv.de/book/download_xml/{0}'

def link_work(dbsession, person, dta_id, source):
    """Link a single work identified by the ``dta_id``."""
    response = requests.get(WORK_TEI_HEADER_URL.format(dta_id))
    if response.status_code == 200:
        doc = etree.fromstring(response.text)
        full_title = ' - '.join([t.text for t in doc.xpath('/teiHeader/fileDesc/titleStmt/title')])
        license = doc.xpath('//licence/@target')
        if license:
            license = re.search('licenses/([a-zA-Z\\-]+)/([0-9]+\\.[0-9]+)', license[0])
            if license:
                license = 'cc-{0}-{1}'.format(license.group(1), license.group(2))
        work = merge_work(dbsession, person, full_title, source)
        if license and license.startswith('cc-'):
            merge_work_property(dbsession, work, '{0}§provider'.format(dta_id), {'label': 'Deutsches Textarchiv',
                                                                                 'value': WORK_HTML_URL.format(dta_id)}, source)
            merge_work_property(dbsession, work, '{0}§data'.format(dta_id), {'value': WORK_TEI_URL.format(dta_id)}, source)
            merge_work_property(dbsession, work, '{0}§license'.format(dta_id), {'value': license}, source)
            merge_work_property(dbsession, work, '{0}§license_url'.format(dta_id), {'value': 'http://www.deutschestextarchiv.de/doku/nutzungsbedingungen'}, source)
