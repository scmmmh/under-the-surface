#!/usr/bin/env python3
import click

from loader import add_people
from editor import edit
from wikidata_link import link_to_wikidata


@click.group()
def main():
    """Under-the-Surface Administration Tool"""


main.add_command(add_people)
main.add_command(edit)
main.add_command(link_to_wikidata)

if __name__ == '__main__':
    main()
