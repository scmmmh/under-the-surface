import re

from datetime import datetime
from hashlib import sha256


def startswith(string, prefix):
    """Checks if the ``string`` starts with the ``prefix``."""
    return string.startswith(prefix)


def split(string, separator):
    """Splits the ``string`` by the ``separator``."""
    return string.split(separator)


def format(string, *args, **kwargs):
    """Format the ``string`` using new-style Python formatting."""
    return string.format(*args, **kwargs)


def json_strftime(timestamp):
    """Timestamp formatting that takes into account missing data."""
    match = re.match('([+-]?)([0-9]{4})-([0-9]{2})-([0-9]{2})T([0-9]{2}):([0-9]{2}):([0-9]{2})Z', timestamp)
    if match:
        parts = [int(p) for p in match.groups()[1:]]
        if parts[3] == 0 and parts[4] == 0 and parts[5] == 0:
            for idx in range(2, -1, -1):
                try:
                    ts = datetime(*parts)
                    if idx == 2:
                        return ts.strftime('%d.%m.%Y')
                    elif idx == 1:
                        return ts.strftime('%m.%Y')
                    elif idx == 0:
                        return ts.strftime('%Y')
                except:
                    parts[idx] = 1
        else:
            for idx in range(5, -1, -1):
                try:
                    ts = datetime(*parts)
                    if idx == 5:
                        return ts.strftime('%d.%m.%Y %H:%M:%S')
                    elif idx == 4:
                        return ts.strftime('%d.%m.%Y %H:%M')
                    elif idx == 3:
                        return ts.strftime('%d.%m.%Y %H')
                    elif idx == 2:
                        return ts.strftime('%d.%m.%Y')
                    elif idx == 1:
                        return ts.strftime('%m.%Y')
                    elif idx == 0:
                        return ts.strftime('%Y')
                except:
                    if idx >= 3:
                        parts[idx] = 0
                    else:
                        parts[idx] = 1
    return ''


def sha256_hash(text):
    hash = sha256()
    hash.update(text.encode('utf-8'))
    return hash.hexdigest()
