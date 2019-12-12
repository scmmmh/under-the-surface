import click
import json
import os

from models import Person


@click.command()
@click.argument('names', nargs=-1)
@click.pass_context
def add_people(ctx, names):
    """Add new people into the archive"""
    dbsession = ctx.obj['dbsession']
    for name in names:
        if '$' in name:
            name, slug = name.split('$')
        else:
            slug = name.replace(' ', '-').lower()
        person = dbsession.query(Person).filter(Person.slug == slug).first()
        if not person:
            person = Person(slug=slug, title=name, status='unconfirmed')
            dbsession.add(person)
            dbsession.commit()
