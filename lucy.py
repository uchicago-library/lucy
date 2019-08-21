import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request

app = Flask(__name__)

class BasicSentences:
    def __init__(self, tree):
        self.tree = tree
 
    def as_list(self):
        """
            returns:
                e.g., [
                        {
                          'abbreviation': '1.1',
                          'alternate_transcriptions': ['', ...],
                          'breakdowns': [{'translation': '', 'transcription': ''}],
                          'speaker': '',
                          'transcription': '',
                          'translation': ''
                        },
                        ...
                      ]
        """
        basic_sentences = []
        for section in self.tree.findall('.//discourseHierarchy/section'):
            value = section.find('properties/property/property/value')
            if value.text == 'Sentence':
                basic_sentences.append({
                    'abbreviation': self.get_abbreviation(section),
                    'alternate_transcriptions': self.get_alternate_transcriptions(section),
                    'breakdowns': self.get_breakdowns(section),
                    'speaker': self.get_speaker(section),
                    'transcription': self.get_transcription(section),
                    'translation': self.get_translation(section)
                })
        return basic_sentences

    def get_abbreviation(self, section):
        """ abbreviation, e.g., '1.2' """
        ab = section.find('identification').find('abbreviation').text
        ab = re.sub('^[^.]*\.', '', ab)
        return '.'.join([s.lstrip('0') for s in ab.split('.')])
    
    def get_speaker(self, section):
        """ speaker """
        for property in section.iter('property'):
            if property.find('label').text == 'Speaker':
                return property.find('value').text
        return ''
 
    def get_breakdowns(self, section):
        """ breakdown """
        breakdown = []
        for s in section.findall('section[@type="phrase"]'):
            breakdown.append(
                {
                    'translation': s.find('translation').find('content').text,
                    'transcription': s.find('transcription').find('content').text,
                }
            )
        return breakdown
    
    def get_transcription(self, section):
        """ transcription """
        return section.find('transcription').find('content').text
    
    def get_translation(self, section):
        """ translations """
        return section.find('translation').find('content').text
    
    def get_alternate_transcriptions(self, section):
        """ alternate transcriptions. """
        transcriptions = [section.find('transcription').find('content').text]
        try:
            transcriptions.append(section.find('transcription').find('content[@lang="pro"]').text)
        except AttributeError:
            pass
        return transcriptions


class Drills:
    def __init__(self, tree):
        self.tree = tree

    def as_list(self):
        """ [
                {
                    'description': 'What would you say?',
                    'translations': [
                        {
                            'translation': 'You greet a friend, you say',
                            'transcriptions: [
                                'Hasta sáamal.',
                                'Kíimak in wóol.',
                                'Hola suku'un.'
                            ]
                        }
                        ...
                    ]
                }
                ...
            ]
        """
        drills = []
        for section in self.tree.findall('.//discourseHierarchy/section'):
            value = section.find('properties/property/property/value')
            if value.text == 'Drill':
                transcriptions = []
                for transcription in section.findall('section/section/transcription/content'):
                    transcriptions.append(transcription.text)
                drills.append({
                    'description': section.find('description').text,
                    'transcriptions': self.get_transcriptions(section)
                })
        return drills

    def get_translations(self, section):
        translations = []
        for translation in section.findall('section'):
            translations.append({
                'translation': translation.find('translation/content').text,
                'transcriptions': get_transcriptions(translation)
            })
        return translations

    def get_transcriptions(self, section):
        transcriptions = []
        for transcription in section.findall('section/transcription/content'):
            transcriptions.append(transcription.text)
        return transcriptions


class Lesson:
    def __init__(self, tree, section):
        self.tree = tree
        self.section = section
    
    def as_list(self):
        """
            params:
                tree - an xml.etree.ElementTree
            returns: 
                e.g., []
        """
        i = 1
        sections = []
        for section_xml in self.tree.findall('.//discourseHierarchy/section'):
            value = section_xml.find('properties/property/property/value')
            if value.text == ('', 'Sentence', 'Pronunciation', 'Grammar', 'Drill')[self.section]:
                sections.append({
                    'description': self.get_description(section_xml),
                    'index': '{:02}'.format(i) if self.section in (2, 5, 6) else None,
                    'notes': self.get_notes(section_xml),
                    'properties': self.get_properties(section_xml)
                })
                i += 1
        return sections

    def get_description(self, section):
        try:
            return section.find('.//description').text
        except AttributeError:
            return ''

    def get_notes(self, section):
        return [n.text for n in section.findall('.//note')]

    def get_properties(self, section):
        return [
            s.text 
            for s in section.find('properties').findall('.//string') 
            if s.text
        ]

def get_uuids():
    """Get a list of UUIDs for the entire project."""
    uuids = []
    tree = ET.fromstring(
        urllib.request.urlopen(
            'http://pi.lib.uchicago.edu/1001/org/ochre/bccb5942-7768-4c0d-aa20-b78bcc970bac'
        ).read()
    )
    for el in tree.findall('.//text[@uuid]'):
        uuids.append(el.get('uuid'))
    return uuids

def get_title(tree, section):
    # e.g., extract the integer 1 from the string "Lesson 01"
    lesson_number = int(tree.find('.//ochre/text/identification/label').text.split()[1].lstrip("0"))
    return 'Lesson {}: {}'.format(
        lesson_number,
        (
            'Front Matter',
            'Basic Sentences',
            'Pronunciation',
            'Grammar',
            'Drills',
            'Listening In',
            'Conversation',
            'Vocabulary',
            'Supplementary Materials',
            'Teaching Aids'
        )[section]
    )

def get_lesson_index(data, uuid):
    for i, record in enumerate(data):
        if record['uuid'] == uuid:
            return i + 1
    raise ValueError

@app.route("/")
def lucy():
    uuid = request.args.get('uuid', default='0ad43a89-09d6-4292-88cb-b6fd6dfe41e5')
    section = int(request.args.get('section', default=0))

    ochre_xml = ET.ElementTree(
        file=urllib.request.urlopen(
            'http://ochre.lib.uchicago.edu/ochre?uuid={}'.format(uuid)
        )
    )

    if section == 0:
        return render_template(
            'front_matter.html',
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
    elif section == 1:
        return render_template(
            'basic_sentences.html',
            basic_sentences=BasicSentences(ochre_xml).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
    elif section == 4:
        return render_template(
            'drills.html',
            blocks=Drills(ochre_xml).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
    else:
        return render_template(
            'lesson_section.html',
            blocks=Lesson(ochre_xml, section).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
 

if __name__ == "__main__":
    app.run()
