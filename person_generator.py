import requests

from lxml import etree
from pelican import signals
from pelican.contents import Content
from pelican.generators import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from scripts.models import Person as DBPerson


class Person(Content):
    """The Person represents the content to be displayed for an individual person."""

    mandatory_properties = ('title',)
    allowed_statuses = ('published')
    default_status = 'published'
    default_template = 'person'

    def __init__(self, content, metadata=None, settings=None, source_path=None, context=None):
        super().__init__(content, metadata=metadata, settings=settings, source_path=source_path, context=context)

    @property
    def first_title_letter(self):
        if 'title' in self.metadata:
            return self.metadata['title'][0]
        else:
            return ''

    @property
    def sources(self):
        """Dynamically generate the list of sources used, based on sources defined on properties and works."""
        sources = {}
        for property in self.metadata.values():
            if isinstance(property, list):
                for value in property:
                    if 'sources' in value:
                        for source in value['sources']:
                            if source['url'] in sources:
                                sources[source['url']]['timestamps'].add(source['timestamp'].strftime('%Y-%m-%dT00:00:00Z'))
                            else:
                                sources[source['url']] = {'label': source['label'],
                                                          'url': source['url'],
                                                          'timestamps': set([source['timestamp'].strftime('%Y-%m-%dT00:00:00Z')])}
                    if 'copies' in value:
                        for copy in value['copies'].values():
                            for value in copy.values():
                                if 'sources' in value:
                                    for source in value['sources']:
                                        if source['url'] in sources:
                                            sources[source['url']]['timestamps'].add(source['timestamp'].strftime('%Y-%m-%dT00:00:00Z'))
                                        else:
                                            sources[source['url']] = {'label': source['label'],
                                                                      'url': source['url'],
                                                                      'timestamps': set([source['timestamp'].strftime('%Y-%m-%dT00:00:00Z')])}
        return sources


class PersonGenerator(Generator):
    """The PersonGenerator generates the person pages from the database, rather than from the filesystem."""

    def __init__(self, context, settings, path, theme, output_path, readers_cache_name='', **kwargs):
        super().__init__(context, settings, path, theme, output_path, readers_cache_name=readers_cache_name, **kwargs)
        engine = create_engine('sqlite:///content/people/database.sqlite')
        self._dbsession = sessionmaker(bind=engine)()
        self.people = []

        signals.page_generator_init.send(self)

    def load_person(self, db_person):
        """Load an individual person's data from the database."""
        _ = self.settings['translate']
        metadata = {'slug': db_person.slug,
                    'title': db_person.title,
                    'verification': 'none'}
        if db_person.status == 'confirmed':
            verification = 2
        elif db_person.status == 'incorrect':
            verification = -1
        else:
            verification = 0
        for db_property in db_person.display_properties:
            if db_property.value.lang is None or db_property.value.lang == self.settings['DEFAULT_LANG']:
                if db_property.name not in metadata:
                    metadata[db_property.name] = []
                property = {'value': db_property.value.value,
                            'label': db_property.value.label,
                            'sources': [{'label': st.source.label, 'url': st.source.url, 'timestamp': st.timestamp}
                                        for st in db_property.sources]}
                metadata[db_property.name].append(property)
                if db_property.status == 'confirmed' and verification >= 0:
                    verification = 2 if verification == 2 else 1
                elif verification == 2:
                    verification = 1
        for db_work in db_person.display_works:
            if 'work' not in metadata:
                metadata['work'] = []
            work = {'title': db_work.title,
                    'category': _('Uncategorised'),
                    'year': 10000,
                    'copies': {}}
            if db_work.status == 'confirmed' and verification >= 0:
                verification = 2 if verification == 2 else 1
            elif verification == 2:
                verification = 1
            for db_property in db_work.display_properties:
                copy_id, facet = db_property.name.split('§')
                if copy_id not in work['copies']:
                    work['copies'][copy_id] = {}
                work['copies'][copy_id][facet] = {'value': db_property.value.value,
                                                  'label': db_property.value.label,
                                                  'sources': [{'label': st.source.label, 'url': st.source.url, 'timestamp': st.timestamp}
                                                              for st in db_property.sources]}
                if db_property.status == 'confirmed' and verification >= 0:
                    verification = 2 if verification == 2 else 1
                elif verification == 2:
                    verification = 1
            metadata['work'].append(work)
        if 'summary' in metadata:
            content = ''.join(['<p>{0}</p>'.format(p['value']) if not p['value'].startswith('<p>') else p['value'] for p in metadata['summary']])
        else:
            content = ''
        if verification == 2:
            metadata['verification'] = 'full'
        elif verification == 1:
            metadata['verification'] = 'partial'
        elif verification == -1:
            metadata['verification'] = 'failed'
        else:
            metadata['verification'] = 'none'
        return Person(content, metadata=metadata, settings=self.settings, context=self.context)


    def generate_context(self):
        """Generate the context, loading all people from the database."""
        self.people = [self.load_person(db_person) for db_person in self._dbsession.query(DBPerson).filter(DBPerson.status != 'incorrect')]
        self._update_context(('people',))

        signals.page_generator_finalized.send(self)

    def generate_output(self, writer):
        """Write the people to the filesystem."""
        for person in self.people:
            writer.write_file(
                person.save_as, self.get_template(person.template),
                self.context, page=person,
                relative_urls=self.settings['RELATIVE_URLS'],
                override_output=hasattr(person, 'override_save_as'),
                url=person.url)

        signals.page_writer_finalized.send(self, writer=writer)


def get_generator(pelican_object):
    """Return the PersonGenerator to be used to generate the person pages"""
    return PersonGenerator


def add_default_settings(pelican_object):
    """Add the required default settings for the person generation."""
    if 'PERSON_SAVE_AS' not in pelican_object.settings:
        pelican_object.settings['PERSON_SAVE_AS'] = 'people/{slug}.html'
    if 'PERSON_URL' not in pelican_object.settings:
        pelican_object.settings['PERSON_URL'] = 'people/{slug}.html'


def register():
    """Register the required signals."""
    signals.initialized.connect(add_default_settings)
    signals.get_generators.connect(get_generator)
