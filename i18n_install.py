from pelican import signals
from gettext import translation


def install_gettext(generator):
    """Install the gettext translator for the current default language."""
    generator.env.install_gettext_translations(translation('under-the-surface',
                                                           localedir='i18n',
                                                           languages=[generator.settings['DEFAULT_LANG']],
                                                           fallback=True))


def register():
    """Register the gettext installation"""
    signals.generator_init.connect(install_gettext)
