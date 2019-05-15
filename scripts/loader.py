import click
import json
import os


@click.command()
@click.argument('names', nargs=-1)
def add_people(names):
    """Add new people into the archive"""
    next_id = 1
    for basepath, directories, files in os.walk(os.path.join('content', 'people')):
        for filename in files:
            if filename.endswith('.json'):
                next_id = max(next_id, int(filename[:4]) + 1)
    for name in names:
        str_id = '{0:04d}'.format(next_id)
        dirname = os.path.join('content', 'people', str_id[0], str_id[1], str_id[2])
        for lang in ['en', 'de']:
            filename = '{0}.{1}.json'.format(os.path.join(dirname, str_id), lang)
            if not os.path.exists(dirname):
                os.makedirs(dirname)
            with open(filename, 'w') as out_f:
                stub = {
                    'data': {
                        'type': 'people',
                        'id': str(next_id),
                        'attributes': {
                            'slug': '{0}-{1}'.format(next_id, name.replace(' ', '-').lower()),
                            'title': name,
                            'template': 'person',
                            'lang': lang
                        }
                    }
                }
                json.dump(stub, out_f, indent=2)
        next_id = next_id + 1
