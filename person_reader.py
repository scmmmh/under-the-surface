import os
import re

from json import load

from pelican import signals
from pelican.readers import BaseReader

from pelicanconf import DEFAULT_LANG


class MultiLanguageJsonapiReader(BaseReader):
    enabled = True
    file_extensions = ['json']

    def read(self, filename):
        metadata = {
            'lang': self.settings['DEFAULT_LANG'],
            'type': 'person'
        }
        path, basename = os.path.split(filename)
        with open(filename) as in_f:
            obj = load(in_f)
            metadata.update(obj['data']['attributes'])
        if 'title' in metadata:
            metadata['firsttitleletter'] = metadata['title'][0]
        else:
            metadata['firsttitleletter'] = ''
        content = ''
        if 'content' in metadata:
            content = ''.join(['<p>{0}</p>'.format(c) for c in metadata['content']])
            del metadata['content']
        if metadata['lang'] != self.settings['DEFAULT_LANG']:
            metadata['Status'] = 'draft'
        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        return content, parsed


def add_reader(readers):
    readers.reader_classes['json'] = MultiLanguageJsonapiReader


def register():
    signals.readers_init.connect(add_reader)
