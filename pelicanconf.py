#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

# Site defaults
AUTHOR = 'Mark Hall'
SITENAME = 'Under the Surface'
SITE_TAGLINE = 'Authors in hiding from the Canon'
BASE_SITEURL = ''
SITEURL = ''

# Path configuration
PATH = 'content'

PAGE_PATHS = ['people', 'pages']

ARTICLE_PATHS = ['articles']
ARTICLE_URL = 'articles/{slug}.html'
ARTICLE_SAVE_AS = 'articles/{slug}.html'

# Internationalisation
TIMEZONE = 'Europe/Berlin'

DEFAULT_LANG = 'en'
LANGUAGES = (
    ('de', 'Deutsch'),
    ('en', 'English'),
)
LANGUAGE_LABELS = dict(LANGUAGES)

# Plugins
PLUGINS = ('person_reader', )

# Theme configuration
THEME = './theme'
PERSON_METADATA = (
    ('Names', 'names'),
    ('Sex or Gender', 'gender'),
    ('Country of Citizenship', 'country_of_citizenship'),
    ('Date of Birth', 'date_of_birth'),
    ('Location of Birth', 'location_of_birth'),
    ('Date of Death', 'date_of_death'),
    ('Location of Death', 'location_of_death'),
    ('Residence', 'residence'),
    ('Languages used', 'languages_used'),
    ('Occupation', 'occupation'),
    ('Field of Work', 'field_of_work'),
    ('Religion', 'religion'),
    ('Religious Order', 'religious_order'),
    ('Canonisation Status', 'canonisation_status'),
)
PERSON_LINK_CATEGORIES = (
    ('Wikidata', 'wikidata'),
    ('Wikipedia', 'wikipedia'),
    ('VIAF', 'viaf'),
    ('GND', 'gnd'),
)

DEFAULT_PAGINATION = 10

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = []

# Social widget
SOCIAL = []

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
