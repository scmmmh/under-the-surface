from json import load

from pelican import signals
from pelican.readers import BaseReader


class JsonApiReader(BaseReader):
    enabled = True
    file_extensions = ['json']

    def read(self, filename):
        metadata = {}
        with open(filename) as in_f:
            obj = load(in_f)
            metadata = obj['data']['attributes']
        parsed = {}
        for key, value in metadata.items():
            parsed[key] = self.process_metadata(key, value)

        return '', parsed

def add_reader(readers):
    readers.reader_classes['json'] = JsonApiReader

def register():
    signals.readers_init.connect(add_reader)
