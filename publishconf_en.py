#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

import os
import sys
sys.path.append(os.curdir)
from publishconf import *

# If your site is available via HTTPS, make sure SITEURL begins with https://
BASE_SITEURL = SITEURL
SITEURL = '{0}/en'.format(SITEURL)
DEFAULT_LANG = 'en'
OUTPUT_PATH = 'output/en'
