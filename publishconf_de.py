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
    ('Namen', 'names', 'string'),
    ('Geschlecht', 'gender', 'string'),
    ('Staatsbürgerschaft', 'country_of_citizenship', 'string'),
    ('Geburtsdatum', 'date_of_birth', 'timestamp'),
    ('Geburtsort', 'location_of_birth', 'string'),
    ('Sterbedatum', 'date_of_death', 'timestamp'),
    ('Sterbeort', 'location_of_death', 'string'),
    ('Residenz', 'residence', 'string'),
    ('Genutzte Sprachen', 'languages_used', 'string'),
    ('Beschäftigung', 'occupation', 'string'),
    ('Aktiviätsbereich', 'field_of_work', 'string'),
    ('Religion', 'religion', 'string'),
    ('Religiöser Orden', 'religious_order', 'string'),
    ('Kanonisierungsstatus', 'canonisation_status', 'string'),
)
