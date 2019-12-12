import click
import json
import os

from models import Person
from util import merge_property


@click.command()
@click.option('--name', prompt='Your name')
@click.option('--email', prompt='Your email')
@click.argument('names', nargs=-1)
@click.pass_context
def add_people(ctx, name, email, names):
    """Add new people into the archive"""
    source = {'label': name, 'url': 'mailto:{0}'.format(email)}
    dbsession = ctx.obj['dbsession']
    for name in names:
        if '$' in name:
            name, slug = name.split('$')
        else:
            slug = name.replace(' ', '-').lower()
        person = dbsession.query(Person).filter(Person.slug == slug).first()
        if not person:
            person = Person(slug=slug, title=name)
            dbsession.add(person)
            dbsession.commit()
        merge_property(dbsession, person, 'name', name, source)
