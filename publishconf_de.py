#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os
import sys
sys.path.append(os.curdir)
from publishconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
BASE_SITEURL = SITEURL
SITEURL = '{0}/de'.format(SITEURL)
DEFAULT_LANG = 'de'
OUTPUT_PATH = 'output/de'

SITENAME = 'Unter der Oberfläche'
SITE_TAGLINE = 'Vor dem Kanon versteckte Autor/in/en'
PERSON_METADATA = (
    ('Namen', 'names'),
    ('Geschlecht', 'gender'),
    ('Staatsbürgerschaft', 'country_of_citizenship'),
    ('Geburtsdatum', 'date_of_birth'),
    ('Geburtsort', 'location_of_birth'),
    ('Sterbedatum', 'date_of_death'),
    ('Sterbeort', 'location_of_death'),
    ('Residenz', 'residence'),
    ('Genutzte Sprachen', 'languages_used'),
    ('Beschäftigung', 'occupation'),
    ('Aktiviätsbereich', 'field_of_work'),
    ('Religion', 'religion'),
    ('Religiöser Orden', 'religious_order'),
    ('Kanonisierungsstatus', 'canonisation_status'),
)
