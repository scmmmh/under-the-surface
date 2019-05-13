import os
import re

from json import load

from pelican import signals
from pelican.readers import BaseReader

from pelicanconf import DEFAULT_LANG, LANGUAGES


class MultiLanguageJsonapiReader(BaseReader):
    enabled = True
    file_extensions = ['{0}.overlay'.format(lang) for lang in LANGUAGES]

    def read(self, filename):
        metadata = {
            'lang': DEFAULT_LANG
        }
        path, basename = os.path.split(filename)
        match = re.match('([0-9]{4})\.([a-z]+)\.overlay', basename)
        if match:
            metadata['lang'] = match.group(2)
            with open(os.path.join(path, '{0}.json'.format(match.group(1)))) as in_f:
                obj = load(in_f)
                metadata.update(obj['data']['attributes'])
        with open(filename) as in_f:
            obj = load(in_f)
            metadata.update(obj['data']['attributes'])
        content = ''
        if 'content' in metadata:
            content = ''.join(['<p>{0}</p>'.format(c) for c in metadata['content']])
            del metadata['content']
        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        return content, parsed


def add_reader(readers):
    readers.reader_classes['overlay'] = MultiLanguageJsonapiReader


def register():
    signals.readers_init.connect(add_reader)
