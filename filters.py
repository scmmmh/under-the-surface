import re

from datetime import datetime


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
