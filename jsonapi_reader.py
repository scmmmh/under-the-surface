from json import load

from pelican import signals
from pelican.readers import BaseReader

from pelicanconf import DEFAULT_LANG


class JsonApiReader(BaseReader):
    enabled = True
    file_extensions = ['json']

    def read(self, filename):
        metadata = {}
        with open(filename) as in_f:
            obj = load(in_f)
            metadata.update(obj['data']['attributes'])
        content = ''
        if 'content' in metadata:
            content = ''.join(['<p>{0}</p>'.format(c) for c in metadata['content'][DEFAULT_LANG]])
            del metadata['content']
        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        return content, parsed

def add_reader(readers):
    readers.reader_classes['json'] = JsonApiReader

def register():
    signals.readers_init.connect(add_reader)
