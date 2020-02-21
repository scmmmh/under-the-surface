import os
import requests
import sys
import traceback

from hashlib import sha256
from lxml import etree
from pelican import signals
from pelican.utils import sanitised_join

from person_generator import PersonGenerator

NS = {'tei': 'http://www.tei-c.org/ns/1.0',
      'room3b': 'https://www.room3b.eu'}

function_ns = etree.FunctionNamespace('https://www.room3b.eu')
id_map = {}

def uid(ctx, seq):
    global id_map
    if seq in id_map:
        id_map[seq] = id_map[seq] + 1
    else:
        id_map[seq] = 1
    return '{0}-{1}'.format(seq, id_map[seq])


function_ns['uid'] = uid

DTA_STYLESHEET = etree.XSLT(etree.XML("""
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:room3b="https://www.room3b.eu">
  <!-- Simplify the name metadata structure -->
  <xsl:template match="tei:persName">
    <tei:persName><xsl:value-of select="tei:forename/text()"/><xsl:text> </xsl:text><xsl:value-of select="tei:surname/text()"/></tei:persName>
  </xsl:template>

  <!-- Merge the front/body/back -->
  <xsl:template match="tei:text">
    <tei:text><tei:body><xsl:apply-templates select="tei:front/*|tei:body/*|tei:back/*" /></tei:body></tei:text>
  </xsl:template>

  <!-- Give each head a unique id -->
  <xsl:template match="tei:head">
    <tei:head>
      <xsl:attribute name="xml:id"><xsl:value-of select="room3b:uid('heading')"/></xsl:attribute>
      <xsl:apply-templates select="@* | node()"/>
    </tei:head>
  </xsl:template>

  <!-- Reformat choices as annotations -->
  <xsl:template match="tei:choice">
    <xsl:variable name="choice_id" select="room3b:uid('choice')"/>
    <tei:ref type="choice"><xsl:attribute name="target">#<xsl:value-of select="$choice_id"/></xsl:attribute><xsl:apply-templates select="tei:corr/* | tei:corr/text()"/></tei:ref>
    <tei:choice>
      <xsl:attribute name="xml:id"><xsl:value-of select="$choice_id"/></xsl:attribute>
      <xsl:apply-templates select="@*"/>
      <xsl:apply-templates select="tei:corr"/>
      <xsl:apply-templates select="tei:sic"/>
    </tei:choice>
  </xsl:template>

  <!-- Drop the following elements -->
  <xsl:template match="tei:fw"/>
  <xsl:template match="tei:pb"/>
  <xsl:template match="tei:gap"/>
  <xsl:template match="tei:milestone"/>

  <xsl:template match="@* | node()">
    <xsl:copy><xsl:apply-templates select="@* | node()"/></xsl:copy>
  </xsl:template>
</xsl:stylesheet>
"""))

TG_EXTRACT_TEXT_STYLESHEET = etree.XSLT(etree.XML("""
<xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:tei="http://www.tei-c.org/ns/1.0" xmlns:room3b="https://www.room3b.eu">
    <xsl:template match="/tei:teiCorpus">
        <xsl:copy-of select="tei:TEI"/>
    </xsl:template>
</xsl:stylesheet>
"""))

def transform_attrib(attrib):
    result = {}
    for key, value in attrib.items():
        if key == 'rendition':
            if value == '#aq':
                result['style'] = 'font-sans-serif'
            elif value == '#b':
                result['style'] = 'font-weight-bold'
            elif value == '#blue':
                result['style'] = 'color-blue'
            elif value == '#c':
                result['style'] = 'text-align-center'
            elif value == '#et':
                result['style'] = 'indent-left-small'
            elif value == '#et2':
                result['style'] = 'indent-left-medium'
            elif value == '#et3':
                result['style'] = 'indent-left-large'
            elif value == '#f':
                result['style'] = 'dotted-border'
            elif value == '#fr':
                result['style'] = 'dotted-border'
            elif value == '#g':
                result['style'] = 'letter-spacing-wide'
            elif value == '#i':
                result['style'] = 'font-style-italic'
            elif value == '#in':
                result['style'] = 'font-size-very-large'
            elif value == '#k':
                result['style'] = 'font-variant-small-caps'
            elif value == '#larger':
                result['style'] = 'font-size-large'
            elif value == '#red':
                result['style'] = 'font-size-red'
            elif value == '#right':
                result['style'] = 'text-align-right'
            elif value == '#s':
                result['style'] = 'text-decoration-line-through'
            elif value == '#smaller':
                result['style'] = 'font-size-small'
            elif value == '#sub':
                result['style'] = 'subscript'
            elif value == '#sup':
                result['style'] = 'superscript'
            elif value == '#u':
                result['style'] = 'text-decoration-underline'
            elif value == '#uu':
                result['style'] = 'text-decoration-double-underline'
            elif value == '#hr':
                result['style'] = 'horizontal-rule'
            else:
                print(value)
        else:
            result[key] = value
    return result


def transform_node(node):
    transformed_node = etree.Element(node.tag, **transform_attrib(node.attrib))
    if node.text and node.text.strip():
        tmp = etree.Element('{http://www.tei-c.org/ns/1.0}seg')
        tmp.text = node.text
        transformed_node.append(tmp)
    for child in node:
        transformed_node.append(transform_node(child))
        if child.tail and child.tail.strip():
            tmp = etree.Element('{http://www.tei-c.org/ns/1.0}seg')
            tmp.text = child.tail
            transformed_node.append(tmp)
    return transformed_node


def transform(doc):
    transformed_doc = etree.Element('{http://www.tei-c.org/ns/1.0}TEI')
    transformed_doc.append(doc.xpath('/tei:TEI/tei:teiHeader', namespaces=NS)[0])
    transformed_doc.append(transform_node(doc.xpath('/tei:TEI/tei:text', namespaces=NS)[0]))
    return transformed_doc


TAGS = set()
KNOWN_TAGS = set(('text', 'anchor', 'body', 'byline', 'cell', 'choice', 'cit', 'closer', 'corr', 'div', 'docAuthor',
                  'docDate', 'docEdition', 'docImprint', 'docTitle', 'head', 'hi', 'item', 'l', 'lb', 'lg', 'list',
                  'note', 'p', 'ptr', 'pubPlace', 'publisher', 'quote', 'ref', 'row', 'seg', 'sic', 'sp', 'speaker',
                  'table', 'titlePage', 'titlePart'))
IGNORED_TAGS = set(('fw', 'pb', 'gap', 'milestone'))


def determine_tags(node):
    global TAGS
    TAGS.add(node.tag[29:])
    for child in node:
        determine_tags(child)


def fetch_cached_work(url):
    hash = sha256()
    hash.update(url.encode('utf-8'))
    os.makedirs('.cache', exist_ok=True)
    filename = os.path.join('.cache', '{0}.tei'.format(hash.hexdigest()))
    if os.path.exists(filename):
        with open(filename, 'rb') as in_f:
            return in_f.read()
    else:
        response = requests.get(url)
        if response.status_code == 200:
            with open(filename, 'wb') as out_f:
                out_f.write(response.content)
            return response.content
        return None


def add_readable_works(generator):
    if isinstance(generator, PersonGenerator):
        for person in generator.people:
            if 'work' in person.metadata:
                for work in person.metadata['work']:
                    for copy in work['copies'].values():
                        if 'provider' in copy and 'data' in copy:
                            if copy['provider']['value'] == 'https://textgridrep.org':
                                content = fetch_cached_work(copy['data']['value'])
                                if content:
                                    doc = etree.XML(content)
                                    doc = DTA_STYLESHEET(transform(TG_EXTRACT_TEXT_STYLESHEET(doc)))
                                    determine_tags(doc.xpath('/tei:TEI/tei:text', namespaces=NS)[0])
                                    hash = sha256()
                                    hash.update(work['title'].encode('utf-8'))
                                    hash.update(b'$$')
                                    hash.update(copy['data']['value'].encode('utf-8'))
                                    copy['read_url'] = {'value': '{0}/{1}.tei'.format(person.url[:-5], hash.hexdigest()), 'label': None}

                                    target_dir = sanitised_join(generator.settings['OUTPUT_PATH'], person.url[:-5])
                                    os.makedirs(target_dir, exist_ok=True)
                                    with open(sanitised_join(target_dir, '{0}.tei'.format(hash.hexdigest())), 'wb') as out_f:
                                        out_f.write(etree.tostring(doc, pretty_print=True))
                            elif copy['provider']['label'] == 'Deutsches Textarchiv':
                                content = fetch_cached_work(copy['data']['value'])
                                if content:
                                    doc = etree.XML(content)
                                    doc = DTA_STYLESHEET(transform(doc))
                                    determine_tags(doc.xpath('/tei:TEI/tei:text', namespaces=NS)[0])
                                    hash = sha256()
                                    hash.update(work['title'].encode('utf-8'))
                                    hash.update(b'$$')
                                    hash.update(copy['data']['value'].encode('utf-8'))
                                    copy['read_url'] = {'value': '{0}/{1}.tei'.format(person.url[:-5], hash.hexdigest()), 'label': None}

                                    target_dir = sanitised_join(generator.settings['OUTPUT_PATH'], person.url[:-5])
                                    os.makedirs(target_dir, exist_ok=True)
                                    with open(sanitised_join(target_dir, '{0}.tei'.format(hash.hexdigest())), 'wb') as out_f:
                                        out_f.write(etree.tostring(doc, pretty_print=True))
    tmp = list(TAGS - KNOWN_TAGS - IGNORED_TAGS)
    tmp.sort()
    for tag in tmp:
        print(tag)


def register():
    """Register the required signals."""
    signals.page_generator_finalized.connect(add_readable_works)
