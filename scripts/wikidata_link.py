import click
import json
import os
import requests


@click.command()
def link_to_wikidata():
    """Link all people to Wikidata"""
    for basepath, _, files in os.walk(os.path.join('content', 'people')):
        for filename in files:
            if filename.endswith('.json'):
                with open(os.path.join(basepath, filename)) as in_f:
                    obj = json.load(in_f)
                if 'links' not in obj['data']['attributes'] or 'wikidata' not in obj['data']['attributes']['links']:
                    obj = load_core_wikidata_data(obj)
                    with open(os.path.join(basepath, filename), 'w') as out_f:
                        json.dump(obj, out_f, indent=2)
                load_language_overlays(basepath, obj, ['en', 'de'])


QUERY_URL = 'https://www.wikidata.org/w/api.php?action=query&list=search&srsearch={0}&format=json'
DETAILS_URL = 'https://www.wikidata.org/wiki/Special:EntityData/{0}.json'


def load_core_wikidata_data(obj):
    """Load a single person by querying Wikidata"""
    response = requests.get(QUERY_URL.format(obj['data']['attributes']['title']))
    if response.status_code == 200:
        data = response.json()
        for result in data['query']['search']:
            response2 = requests.get(DETAILS_URL.format(result['title']))
            if response2.status_code == 200:
                data2 = response2.json()['entities'][result['title']]
                human = False
                if 'P31' in data2['claims']:
                    for tmp in data2['claims']['P31']:
                        if tmp['mainsnak']['datavalue']['value']['id'] == 'Q5':
                            human = True
                if human:
                    set_data(obj, ('data', 'attributes', 'links', 'wikidata'), [result['title']])
                    # Load external links
                    for key, name in [('P214', 'viaf'), ('P227', 'gnd')]:
                        if key in data2['claims']:
                            if name not in obj['data']['attributes']['links']:
                                obj['data']['attributes']['links'][name] = []
                            for claim in data2['claims'][key]:
                                obj['data']['attributes']['links'][name].append(claim['mainsnak']['datavalue']['value'])
                    break
    return obj


def load_language_overlays(basepath, obj, languages):
    """Load the language overlay data. Mainly names"""
    for lang in languages:
        filename = os.path.join(basepath, '{0:04d}.{1}.overlay'.format(int(obj['data']['id']), lang))
        if not os.path.exists(filename):
            response = requests.get(DETAILS_URL.format(obj['data']['attributes']['links']['wikidata'][0]))
            if response.status_code == 200:
                data = response.json()['entities'][obj['data']['attributes']['links']['wikidata'][0]]
                obj2 = {'data': {'attributes': {}}}
                # Load core name
                if 'name' not in obj2['data']['attributes']:
                    obj2['data']['attributes']['names'] = []
                for value in data['labels'].values():
                    if value['language'] == lang:
                        obj2['data']['attributes']['names'].append(value['value'])
                # Load alternative name
                for value_list in data['aliases'].values():
                    for value in value_list:
                        if value['language'] == lang:
                            obj2['data']['attributes']['names'].append(value['value'])
                # Load content
                if 'content' not in obj2['data']['attributes']:
                    obj2['data']['attributes']['content'] = []
                for value in data['descriptions'].values():
                    if value['language'] == lang:
                        obj2['data']['attributes']['content'].append(value['value'])
                with open(filename, 'w') as out_f:
                    json.dump(obj2, out_f, indent=2)



def set_data(obj, path, data):
    """Set data in the object at the given path"""
    if len(path) == 1:
        obj[path[0]] = data
    else:
        if path[0] not in obj:
            obj[path[0]] = {}
        set_data(obj[path[0]], path[1:], data)
