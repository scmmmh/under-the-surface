from datetime import datetime


def get_attribute(obj, path, default=None):
    """Get the value in obj at path."""
    if isinstance(path, str):
        path = path.split('.')
    if path:
        if path[0] in obj:
            if len(path) == 1:
                return obj[path[0]]
            else:
                return get_attribute(obj[path[0]], path[1:], default=default)
    return default


def set_value(obj, path, value, source):
    """Set the value at path in obj."""
    if isinstance(path, str):
        path = path.split('.')
    tmp = obj
    for component in path[:-1]:
        if component not in tmp:
            tmp[component] = {}
        tmp = tmp[component]
    if path[-1] not in tmp:
        tmp[path[-1]] = {}
    if source:
        tmp[path[-1]] = {'value': value,
                         'source': source['source'],
                         'timestamp': source['timestamp']}
    else:
        tmp[path[-1]] = value


def add_to_set(obj, path, value, source):
    """Add a value to the set at location path in obj."""
    if isinstance(path, str):
        path = path.split('.')
    tmp = obj
    for component in path[:-1]:
        if component not in tmp:
            tmp[component] = {}
        tmp = tmp[component]
    if path[-1] not in tmp:
        tmp[path[-1]] = []
    elif not isinstance(tmp[path[-1]], list):
        tmp[path[-1]] = [tmp[path[-1]]]
    found = False
    for exist in tmp[path[-1]]:
        if exist['value'] == value:
            exist['source'] = source['source']
            exist['timestamp'] = source['timestamp']
            found = True
    if not found:
        tmp[path[-1]].append({'value': value,
                              'source': source['source'],
                              'timestamp': source['timestamp']})


def get_xml_attribute(obj, path, default=None, ns=None):
    if isinstance(path, str):
        path = path.split('.')
    if path:
        if path[0].startswith('@'):
            if path[0][1:] in obj.attrib:
                return obj.attrib[path[0][1:]]
        elif path[0] == 'text()':
            return obj.text
        else:
            for child in obj:
                if ns:
                    tag = '{ns}:{tag}'.format(ns=ns[child.tag[:child.tag.find('}') + 1]],
                                              tag=child.tag[child.tag.find('}') + 1:])
                else:
                    tag = child.tag
                if tag == path[0]:
                    if len(path) == 1:
                        return child
                    else:
                        return get_xml_attribute(child, path[1:], default=default, ns=ns)
    return default


def json_utcnow():
    return datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
