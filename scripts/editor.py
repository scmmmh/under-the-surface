import click
import json
import os


@click.command()
@click.option('--set', '-s', nargs=2, type=str, multiple=True, help="Set the attribute to the given value")
@click.option('--unset', '-u', nargs=1, type=str, multiple=True, help="Remove the given attribute")
@click.option('--add', '-a', nargs=2, type=str, multiple=True, help="Add a value to the given attribute")
@click.option('--remove', '-r', nargs=2, type=str, multiple=True, help="Remove a value from the given attribute")
@click.argument('person-id', type=int)
def edit(set, unset, add, remove, person_id):
    """Edit a single person"""
    file_id = '{:04d}'.format(person_id)
    filepath = '{0}.json'.format(os.path.join('content', 'people', file_id[:2], file_id))
    if os.path.exists(filepath):
        with open(filepath) as in_f:
            data = json.load(in_f)
        for key, value in set:
            data['data']['attributes'][key] = value
        for key in unset:
            if key in data['data']['attributes']:
                del data['data']['attributes'][key]
        for key, value in add:
            if key in data['data']['attributes']:
                if isinstance(data['data']['attributes'][key], list):
                    data['data']['attributes'][key].append(value)
                else:
                    data['data']['attributes'][key] = [data['data']['attributes'][key], value]
            else:
                data['data']['attributes'][key] = [value]
        for key, value in remove:
            if key in data['data']['attributes']:
                if isinstance(data['data']['attributes'][key], list):
                    if value in data['data']['attributes'][key]:
                        data['data']['attributes'][key].remove(value)
                    if not data['data']['attributes'][key]:
                        del data['data']['attributes'][key]
                else:
                    del data['data']['attributes'][key]
        with open(filepath, 'w') as out_f:
            json.dump(data, out_f)
