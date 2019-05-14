#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = 'Mark Hall'
SITENAME = 'Under the Surface'
SITEURL = ''

PATH = 'content'

PAGE_PATHS = ['people', 'pages']

ARTICLE_PATHS = ['articles']
ARTICLE_URL = 'articles/{slug}.html'
ARTICLE_SAVE_AS = 'articles/{slug}.html'

TIMEZONE = 'Europe/Berlin'

LANGUAGES = ['en', 'de']
DEFAULT_LANG = 'en'

PLUGINS = ('person_reader', )

THEME = './theme'
PERSON_METADATA = (
    ('Names', 'names'),
)
PERSON_LINK_CATEGORIES = (
    ('Wikidata', 'wikidata', 'https://www.wikidata.org/wiki/%s'),
    ('VIAF', 'viaf', 'https://viaf.org/viaf/%s/'),
    ('GND', 'gnd', 'https://d-nb.info/gnd/%s')
)

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None

# Blogroll
LINKS = (('Pelican', 'http://getpelican.com/'),
         ('Python.org', 'http://python.org/'),
         ('Jinja2', 'http://jinja.pocoo.org/'),
         ('You can modify those links in your config file', '#'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

# Uncomment following line if you want document-relative URLs when developing
RELATIVE_URLS = True
