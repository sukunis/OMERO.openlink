import sys
from omeroweb.settings import process_custom_settings, report_settings


def str_not_empty(o):
    s = str(o)
    if not o or not s:
        raise ValueError('Invalid empty value')
    return s

def str_allow_empty(o):
    return str(o)


OPENLINK_SETTINGS_MAPPINGS = {
    'omero.web.openlink.dir': ['OPENLINK_DIR', '', str_not_empty, None],
    # $ omero config set omero.web.openlink.dir '{""}'
    'omero.web.openlink.servername': ['SERVER_NAME', '', str_not_empty, None],
    'omero.web.openlink.type_http': ['TYPE_HTTP', '', str_not_empty, None],
    'omero.web.openlink.nginx_location': ['NGINX_LOCATION', '', str_allow_empty, None]
}

process_custom_settings(sys.modules[__name__], 'OPENLINK_SETTINGS_MAPPINGS')
report_settings(sys.modules[__name__])
