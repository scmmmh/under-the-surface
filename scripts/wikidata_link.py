import click
import json
import os
import requests


@click.command()
def link_to_wikidata():
    """Link all people to Wikidata"""
    for basepath, _, files in os.walk(os.path.join('content', 'people')):
        for filename in files:
            with open(os.path.join(basepath, filename)) as in_f:
                obj = json.load(in_f)
            if 'links' not in obj['data']['attributes'] or 'wikidata' not in obj['data']['attributes']['links']:
                obj = link_single_person(obj)
                with open(os.path.join(basepath, filename), 'w') as out_f:
                    json.dump(obj, out_f, indent=2)


QUERY_URL = 'https://www.wikidata.org/w/api.php?action=query&list=search&srsearch={0}&format=json'
DETAILS_URL = 'https://www.wikidata.org/wiki/Special:EntityData/{0}.json'


def link_single_person(obj):
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
                    # Load core name
                    if 'name' not in obj['data']['attributes']:
                        obj['data']['attributes']['name'] = {}
                    for value in data2['labels'].values():
                        if value['language'] not in obj['data']['attributes']['name']:
                            obj['data']['attributes']['name'][value['language']] = []
                        obj['data']['attributes']['name'][value['language']].append(value['value'])
                    # Load alternative name
                    for value_list in data2['aliases'].values():
                        for value in value_list:
                            if value['language'] not in obj['data']['attributes']['name']:
                                obj['data']['attributes']['name'][value['language']] = []
                            obj['data']['attributes']['name'][value['language']].append(value['value'])
                    # Load content
                    if 'content' not in obj['data']['attributes']:
                        obj['data']['attributes']['content'] = {}
                    for value in data2['descriptions'].values():
                        if value['language'] not in obj['data']['attributes']['content']:
                            obj['data']['attributes']['content'][value['language']] = []
                        obj['data']['attributes']['content'][value['language']].append(value['value'])
                    # Load external links
                    for key, name in [('P214', 'viaf'), ('P227', 'gnd')]:
                        if key in data2['claims']:
                            if name not in obj['data']['attributes']['links']:
                                obj['data']['attributes']['links'][name] = []
                            for claim in data2['claims'][key]:
                                obj['data']['attributes']['links'][name].append(claim['mainsnak']['datavalue']['value'])
                    break
    return obj

def set_data(obj, path, data):
    """Set data in the object at the given path"""
    if len(path) == 1:
        obj[path[0]] = data
    else:
        if path[0] not in obj:
            obj[path[0]] = {}
        set_data(obj[path[0]], path[1:], data)
