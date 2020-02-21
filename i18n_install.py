from pelican import signals
from gettext import translation


def install_gettext_jinja2(generator):
    """Install the gettext translator for the current default language."""
    generator.env.install_gettext_translations(translation('under-the-surface',
                                                           localedir='i18n',
                                                           languages=[generator.settings['DEFAULT_LANG']],
                                                           fallback=True))


def install_gettext(pelican_object):
    pelican_object.settings['translate'] = translation('under-the-surface',
                                                       localedir='i18n',
                                                       languages=[pelican_object.settings['DEFAULT_LANG']],
                                                       fallback=True).gettext


def register():
    """Register the gettext installation"""
    signals.initialized.connect(install_gettext)
    signals.generator_init.connect(install_gettext_jinja2)
