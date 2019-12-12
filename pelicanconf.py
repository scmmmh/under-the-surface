#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

from gettext import NullTranslations

from filters import json_strftime


# Dummy Translation to mark strings for translation
_ = NullTranslations().gettext

# Site defaults
AUTHOR = 'Mark Hall'
SITENAME = _('Under the Surface')
SITE_TAGLINE = _('Authors in hiding from the Canon')
BASE_SITEURL = ''
SITEURL = ''

# Path configuration
PATH = 'content'

PAGE_PATHS = ['pages']

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
PLUGINS = ('person_generator', 'i18n_install',)

# Theme configuration
THEME = './theme'
PERSON_METADATA = (
    (_('Names'), 'name', 'string'),
    (_('Sex or Gender'), 'gender', 'string'),
    (_('Country of Citizenship'), 'country_of_citizenship', 'string'),
    (_('Date of Birth'), 'date_of_birth', 'timestamp'),
    (_('Location of Birth'), 'location_of_birth', 'string'),
    (_('Date of Death'), 'date_of_death', 'timestamp'),
    (_('Location of Death'), 'location_of_death', 'string'),
    (_('Residence'), 'residence', 'string'),
    (_('Languages used'), 'languages_used', 'string'),
    (_('Occupation'), 'occupation', 'string'),
    (_('Field of Work'), 'field_of_work', 'string'),
    (_('Religion'), 'religion', 'string'),
    (_('Religious Order'), 'religious_order', 'string'),
    (_('Canonisation Status'), 'canonisation_status', 'string'),
)
PERSON_LINK_CATEGORIES = (
    (_('Wikidata'), 'wikidata'),
    (_('Wikipedia'), 'wikipedia'),
    (_('VIAF'), 'viaf'),
    (_('GND'), 'gnd'),
)
JINJA_FILTERS = {
    'format_timestamp': json_strftime
}
JINJA_ENVIRONMENT = {
    'extensions': ['jinja2.ext.i18n']
}
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
