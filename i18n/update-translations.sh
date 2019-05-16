#!/usr/bin/env bash

pybabel extract --mapping-file babel.cfg --output i18n/under-the-surface.pot *.py theme
pybabel update -i i18n/under-the-surface.pot -l en -d i18n/ -D under-the-surface --ignore-obsolete
pybabel update -i i18n/under-the-surface.pot -l de -d i18n/ -D under-the-surface --ignore-obsolete
