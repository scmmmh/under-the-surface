#!/usr/bin/env python3
import click

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from loader import add_people
from editor import edit
from wikidata_link import link_to_wikidata, load_wikidata_data
from textgrid_link import link_to_textgrid
from dta_link import link_to_dta
from models import Base


@click.group()
@click.pass_context
def main(ctx):
    """Under-the-Surface Administration Tool"""
    ctx.ensure_object(dict)
    engine = create_engine('sqlite:///content/people/database.sqlite')
    Base.metadata.create_all(engine)
    ctx.obj['dbsession'] = sessionmaker(bind=engine)()


main.add_command(add_people)
main.add_command(edit)
main.add_command(link_to_wikidata)
main.add_command(link_to_dta)
main.add_command(link_to_textgrid)

if __name__ == '__main__':
    main()
