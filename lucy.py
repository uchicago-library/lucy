# -*- coding: utf-8 -*-

import json
import re
import sys
import urllib.request
import xml.etree.ElementTree as ET
from flask import Flask, render_template, request
from xml.sax.saxutils import unescape

app = Flask(__name__)

def get_xml_contents(e):
    """Get the contents of a node as a string of text and XML 
       child nodes: e.g, in a <p>, get all of the <em> and 
       <strong> elements, but not the <p> and </p> themselves.
    """
    e_str = ET.tostring(e).decode('utf-8')
    opening_indices = [i for i, c in enumerate(e_str) if c == '<']
    closing_indices = [i for i, c in enumerate(e_str) if c == '>']
    return e_str[closing_indices[0]+1:opening_indices[-1]]

class Lucy:
    def __init__(self, tree):
        self.tree = tree

    def get_description(self, section):
        try:
            return section.find('description').text
        except AttributeError:
            return ''
    

class BasicSentences(Lucy):
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
            if section.findall('.//property/value[@uuid="8754c696-3359-4ecf-8cf5-7e2d293a26b3"]'):
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
                    'translation': self.get_translation(s),
                    'transcription': self.get_transcription(s)
                }
            )
        return breakdown
    
    def get_transcription(self, section):
        """ transcription """
        try:
            return {
                'text': get_xml_contents(section.find('./transcription/content')),
                'uuid': section.find('./transcription/links/resource[@type="audio"]').get('uuid')
            }
        except AttributeError:
            return {'text': '', 'uuid': ''}
    
    def get_translation(self, section):
        """ translations """
        try:
            return {
                'text': get_xml_contents(section.find('./translation/content')),
                'uuid': section.find('./translation/links/resource[@type="audio"]').get('uuid')
            }
        except AttributeError:
            return {'text': '', 'uuid': ''}
    
    def get_alternate_transcriptions(self, section):
        """ alternate transcriptions. """
        transcriptions = []
        for a in ('sup', 'pro'):
            try:
                transcriptions.append(get_xml_contents(section.find('./transcription/content[@lang="' + a + '"]')))
            except AttributeError:
                pass
        return transcriptions


class Pronunciations(Lucy):
    def as_list(self):
        pronunciations = []
        i = 1
        for section in self.tree.findall('.//discourseHierarchy/section'):
            if section.findall(".//property/value[@uuid='eb1d9fc2-3c4d-4615-ab8e-3065aacc57f2']"):
                pronunciations.append({
                    'abbreviation': '{:02d}'.format(i),
                    'description': self.get_description(section),
                    'examples': self.get_examples(section),
                    'notes': self.get_notes(section),
                    'uuid': self.get_uuid(section)
                })
                i += 1
        return pronunciations

    def get_examples(self, section):
        examples = []
        for property in section.findall('./properties//property'):
            if property.find('label').get('uuid') == 'ce77fb10-4473-4fe0-a8b1-ee26f0956dab':
                examples.append(property.find('value').text)
        return examples

    def get_notes(self, section):
        notes = []
        for note in section.findall('./notes/note'):
            notes.append(note.text)
        return notes

    def get_uuid(self, section):
        return section.find('./links/resource[@type="audio"]').get('uuid')


class Grammar(Lucy):
    def as_list(self):
        grammar_blocks = []
        for section in self.tree.findall('.//discourseHierarchy/section'):
            if section.findall('.//property/value[@uuid="fc6b91e0-00f8-4a32-8aed-4934432253de"]'):
                grammar_blocks.append({
                    'description': self.get_description(section),
                    'content': self.get_content(section)
                })
        return grammar_blocks

    def get_description(self, section):
        return section.find('./links/resource').text

    def get_content(self, section):
        uuid = section.find('./links/resource').get('uuid')
        content_xml = ET.ElementTree(
            file=urllib.request.urlopen(
                'http://ochre.lib.uchicago.edu/ochre?uuid={}'.format(uuid)
            )
        )
        return content_xml.find('//document').text

class Drills(Lucy):
    def as_list(self):
        """ 
            returns:
                e.g., [
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
                },
                {
                    'description': 'Variation Drills',
                    'drills': [
                        {
                            'text': '...',
                            'uuid': '...'
                        },
                        {
                            'text': '...',
                            'uuid': '...'
                        }
                        ...
                    ]
                }
                ...
            ]
        """
        drills = []
        for section in self.tree.findall('.//discourseHierarchy/section'):
            if section.findall(".//property/value[@uuid='0a394087-7e9b-4ad9-a97e-97638008bc97']"):
                description = section.find('description').text
                if section.findall(".//section/transcription/links/resource"):
                    drills.append({
                        'description': description,
                        'drills': self.get_drills(section)
                    })
                else:
                    drills.append({
                        'description': description,
                        'translations': self.get_translations(section)
                    })
        return drills

    def get_drills(self, section):
        drills = []
        for s in section.findall('section'):
            column1 = {}
            try:
                column1['text'] = s.findall('section')[0].find('transcription').find('content').text
            except AttributeError:
                column1['text'] = ''
            try:
                column1['uuid'] = s.findall('section')[0].find('transcription').find('links').find('resource').get('uuid')
            except AttributeError:
                pass

            column2 = {}
            try:
                column2['text'] = s.findall('section')[1].find('transcription').find('content').text
            except AttributeError:
                column2['text'] = ''
            try:
                column2['uuid'] = s.findall('section')[1].find('transcription').find('links').find('resource').get('uuid')
            except AttributeError:
                pass
     
            drills.append([column1, column2])
        return drills

    def get_translations(self, section):
        translations = []
        for translation in section.findall('section'):
            try:
                translation_str = translation.find('./translation/content').text
            except AttributeError:
                translation_str = ''
            translations.append({
                'translation': translation_str,
                'transcriptions': self.get_transcriptions(translation)
            })
        return translations

    def get_transcriptions(self, section):
        transcriptions = []
        for transcription in section.findall('section/transcription/content'):
            transcriptions.append(transcription.text)
        return transcriptions


class ListeningIn(Lucy):
    def as_list(self):
        listening_in = []
        i = 1
        for section in self.tree.findall('.//discourseHierarchy/section'):
            if section.findall('.//property/value[@uuid="72eb5e25-0d76-4b70-9c1f-13717a6f9cc5"]'):
                listening_in.append({
                    'abbreviation': '{:02d}'.format(i),
                    'description': section.find('description').text,
                    'transcriptions': self.get_transcriptions(section)
                })
                i += 1
        return listening_in

    def get_transcriptions(self, section):
        transcriptions = []
        for transcription in section.findall('./section/transcription'):
            transcriptions.append({
                'content': transcription.find('content').text, 
                'uuid': transcription.find('./links/resource').get('uuid')
            })
        return transcriptions


class Conversation(Lucy):
    """
    Conversation sections have two different formats. See lessons 1-5 for
    examples of the first, and lessons 6, 12, and 18 for examples of the
    second.
    """

    def as_list(self):
        conversation_blocks = []
        i = 1
        for section in self.tree.findall('.//discourseHierarchy/section'):
            if section.findall('.//property/value[@uuid="c72c2b24-74f2-461a-b4f5-9dae22782da4"]'):
                if section.findall('.//property/value[@uuid="40d5cb3c-b280-4467-8000-947e297a4521"]'):
                    conversation_blocks.append({
                        'abbreviation': '{:02d}'.format(i),
                        'content': self.get_conversation_stimulus(section),
                        'heading': 'Conversation Stimulus'
                    })
                elif section.findall('.//property/value[@uuid="683d06bb-4064-4e94-8cab-6490276636e0"]'):
                    question_and_answer_blocks, situation_narrative_blocks = self.get_situation_narrative(section)
                    conversation_blocks.append({
                        'abbreviation': '{:02d}'.format(i),
                        'question_and_answer_content': question_and_answer_blocks,
                        'situation_narrative_content': situation_narrative_blocks,
                        'heading': 'Situation Narrative'
                    })
                else:
                    conversation_blocks.append({
                        'abbreviation': '{:02d}'.format(i),
                        'description': self.get_description(section),
                        'heading': ''
                    })
                i += 1
        return conversation_blocks

    def get_conversation_stimulus(self, section):
        blocks = []
        for subsection in section.findall('section'):
            blocks.append({
                'character': self.get_character(subsection),
                'prompt': self.get_prompt(subsection),
                'response': self.get_response(subsection)
            })
        return blocks

    def get_character(self, section):
        for subsection in section.findall('section'):
            # response
            if subsection.findall('.//property/value[@uuid="7697db70-3d11-442c-a17b-11339635f0e8"]'):
                # speaker
                for prop in subsection.findall('.//property'):
                    if prop.find('label').get('uuid') == '9dc5fbbe-b8db-417f-b9d4-68efa3576e80':
                        return prop.find('value').text
        return ''

    def get_prompt(self, section):
        for subsection in section.findall('section'):
            if subsection.findall('.//property/value[@uuid="4e64b8a2-a91a-48f9-9d5b-eb6259ba7b9b"]'):
                return {
                    'text': subsection.find('transcription').find('content').text,
                    'uuid': subsection.find('transcription').find('links').find('resource').get('uuid')
                }
        return {'text': '', 'uuid': '#'}

    def get_response(self, section):
        for subsection in section.findall('section'):
            if subsection.findall('.//property/value[@uuid="7697db70-3d11-442c-a17b-11339635f0e8"]'):
                return {
                    'text': subsection.find('transcription').find('content').text,
                    'uuid': subsection.find('transcription').find('links').find('resource').get('uuid')
                }
        return {'text': '', 'uuid': '#'}

    def get_situation_narrative(self, section):
        question_and_answer_blocks = []
        situation_narrative_blocks = []
        for subsection in section.findall('section'):
            # question and answer
            if subsection.findall('.//property/value[@uuid="540679da-02c4-45ea-afee-f045dc2724fe"]'):
                for subsubsection in subsection.findall('section'):
                    # prompt
                    if subsubsection.findall('.//property/value[@uuid="4e64b8a2-a91a-48f9-9d5b-eb6259ba7b9b"]'):
                        question_and_answer_block = {}
                        try:
                            question_and_answer_block['prompt'] = {
                                'text': subsubsection.find('transcription').find('content').text,
                                'uuid': subsubsection.find('transcription').find('links').find('resource').get('uuid')
                            }
                        except AttributeError:
                            question_and_answer_block['prompt'] = {
                                'text': '',
                                'uuid': ''
                            }
                    # response
                    elif subsubsection.findall('.//property/value[@uuid="7697db70-3d11-442c-a17b-11339635f0e8"]'):
                        try:
                            question_and_answer_block['response'] = {
                                'text': subsubsection.find('transcription').find('content').text,
                                'uuid': subsubsection.find('transcription').find('links').find('resource').get('uuid')
                            }
                        except AttributeError:
                            question_and_answer_block['response'] = {
                                'text': '',
                                'uuid': ''
                            }
                        question_and_answer_blocks.append(question_and_answer_block)
            else:
                situation_narrative_blocks.append({
                    'translation': self.get_translation(subsection),
                    'transcription': self.get_transcription(subsection)
                })
        return question_and_answer_blocks, situation_narrative_blocks

    def get_transcription(self, section):
        try:
            return {
                'text': section.find('./transcription/content').text,
                'uuid': section.find('./transcription/links/resource[@type="audio"]').get('uuid')
            }
        except AttributeError:
            return {'text': '', 'uuid': ''}
    
    def get_translation(self, section):
        try:
            return {
                'text': section.find('./translation/content').text,
                'uuid': section.find('./translation/links/resource[@type="audio"]').get('uuid')
            }
        except AttributeError:
            return {'text': '', 'uuid': ''}

class Vocabulary(Lucy):
    def as_list(self):
        for section in self.tree.findall('.//discourseHierarchy/section'):
            if section.findall('.//property/value[@uuid="a22fdc12-a968-4da8-b96f-0e48002a8473"]'):
                return self.get_vocabulary_blocks(section)
        return []

    def get_vocabulary_blocks(self, section):
        vocabulary_blocks = []
        for vocabulary in section.findall('section'):
            try:
                vocabulary_blocks.append({
                    'translation': vocabulary.find('./translation/content').text,
                    'transcription': vocabulary.find('./transcription/content').text
                })
            except AttributeError:
                pass
        return vocabulary_blocks


class SupplementaryMaterials(Lucy):
    def as_list(self):
        supplementary_materials = []
        for section in self.tree.findall('.//discourseHierarchy/section'):
            if section.findall('.//property/value[@uuid="59bf3d38-4a2c-45c2-a07b-07e61cc71774"]'):
                pass
        return supplementary_materials


class TeachingAids(Lucy):
    def as_list(self):
        teaching_aids = []
        for section in self.tree.findall('.//discourseHierarchy/section'):
            if section.findall('.//property/value[@uuid="e03bdf4a-d99d-4fb2-9caa-bf0d5f5d7c26"]'):
                pass
        return teaching_aids


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
    """Get section titles."""
    return 'Lesson {}: {}'.format(
        int(tree.find('.//ochre/text/identification/abbreviation').text),
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
    elif section == 2:
        return render_template(
            'pronunciation.html',
            blocks=Pronunciations(ochre_xml).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
    elif section == 3:
        return render_template(
            'grammar.html',
            blocks=Grammar(ochre_xml).as_list(),
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
    elif section == 5:
        return render_template(
            'listening_in.html',
            blocks=ListeningIn(ochre_xml).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
    elif section == 6:
        return render_template(
            'conversation.html',
            blocks=Conversation(ochre_xml).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
    elif section == 7:
        return render_template(
            'vocabulary.html',
            blocks=Vocabulary(ochre_xml).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
    elif section == 8:
        return render_template(
            'supplementary_materials.html',
            blocks=SupplementaryMaterials(ochre_xml).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )
    elif section == 9:
        return render_template(
            'teaching_aids.html',
            blocks=TeachingAids(ochre_xml).as_list(),
            title=get_title(ochre_xml, section),
            uuids=get_uuids()
        )


if __name__ == "__main__":
    app.run()
