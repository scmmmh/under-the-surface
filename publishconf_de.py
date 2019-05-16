#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

from gettext import translation

import os
import sys
sys.path.append(os.curdir)
from publishconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
BASE_SITEURL = SITEURL
SITEURL = '{0}/de'.format(SITEURL)
DEFAULT_LANG = 'de'
OUTPUT_PATH = 'output/de'

t = translation('under-the-surface', localedir='i18n', languages=[DEFAULT_LANG], fallback=True)
_ = t.gettext

SITENAME = _(SITENAME)
SITE_TAGLINE = _(SITE_TAGLINE)
PERSON_METADATA = tuple([(_(label), key, type) for label, key, type in PERSON_METADATA])
