import re
import sys
import urllib.request
from flask import Flask, render_template, request
import xml.etree.ElementTree as ET
app = Flask(__name__)

def get_abbreviation(section):
    """ 'bs 01.02.03' returns '2.3'
    """
    ab = section.find('identification').find('abbreviation').text
    ab = re.sub('^[^.]*\.', '', ab)
    return '.'.join([s.lstrip('0') for s in ab.split('.')])

def get_speaker(section):
    for property in section.iter('property'):
        if property.find('label').text == 'Speaker':
            return property.find('value').text
    return ''

def get_breakdowns(section):
    breakdown = []
    for s in section.findall('section[@type="phrase"]'):
        breakdown.append(
            {
                'translation': s.find('translation').find('content').text,
                'transcription': s.find('transcription').find('content').text,
            }
        )
    return breakdown

def get_transcription(section):
    return section.find('transcription').find('content').text

def get_translation(section):
    return section.find('translation').find('content').text

def get_alternate_transcriptions(section):
    """ alternate transcriptions. """
    transcriptions = [section.find('transcription').find('content').text]
    try:
        transcriptions.append(section.find('transcription').find('content[@lang="pro"]').text)
    except AttributeError:
        pass
    return transcriptions

def get_lesson(tree):
    lesson = []
    for discourseHierarchy in tree.iter('discourseHierarchy'):
        for section in discourseHierarchy.findall('section[@type="sentence"]'):
            lesson.append({
                'abbreviation': get_abbreviation(section),
                'alternate_transcriptions': get_alternate_transcriptions(section),
                'breakdowns': get_breakdowns(section),
                'speaker': get_speaker(section),
                'transcription': get_transcription(section),
                'translation': get_translation(section)
            })
    return lesson


@app.route("/")
def hello():
    uuid = request.args.get('uuid')
    section = request.args.get('section')
    tree = ET.ElementTree(file=urllib.request.urlopen('http://ochre.lib.uchicago.edu/ochre?uuid={}'.format(uuid)))
    print(get_lesson(tree))
    return render_template(
        'index.html',
        lesson=get_lesson(tree)
    )

if __name__ == "__main__":
    app.run()

'''
Lesson 1
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 2
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 3
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 4
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 5
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 6
  Basic Sentences Review
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 7
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 8
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 9
  <li id="menu-1371" class="menu-path-basic_sentences-9"><a href="basic_sentences/9.html">Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 10
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 11
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 12
  Basic Sentences Review
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 13
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 14
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 15
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 16
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 17
  Basic Sentences
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Lesson 18
  Basic Sentences Review
  Pronunciation
  Grammar
  Drills
  Listening In
  Conversation
  Vocabulary
  Supplementary Materials
  Teaching Aids
Reference
  Grammar
  Lexicon
  Blair & Vermont Salas

    lessons = {
        1: "http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5",
        2: "http://ochre.lib.uchicago.edu/ochre?uuid=c3791c4d-8e22-4770-aef8-9b524deda61c",
        3: "http://ochre.lib.uchicago.edu/ochre?uuid=afe870bb-c5d8-4ee1-804a-0da942345f0f",
        4: "http://ochre.lib.uchicago.edu/ochre?uuid=1e591579-2259-4b78-8a5c-5027aa1ecfde",
        5: "http://ochre.lib.uchicago.edu/ochre?uuid=db7cbbe1-229f-4b60-a8f1-35fda8ec9dbd",
        6: "http://ochre.lib.uchicago.edu/ochre?uuid=5855e101-4bbd-4839-8b5e-c02054233654",
        7: "http://ochre.lib.uchicago.edu/ochre?uuid=9c73e504-e9fc-473b-a67c-d21ea10a9291",
        8: "http://ochre.lib.uchicago.edu/ochre?uuid=9679d90a-f936-45da-9c55-33192af0a59d",
        9: "http://ochre.lib.uchicago.edu/ochre?uuid=8643c265-d9ff-4960-a5bc-26a1eb1d772e",
        10: "http://ochre.lib.uchicago.edu/ochre?uuid=9ed29352-7905-4d0d-a6c0-a5dedee82c2b",
        11: "http://ochre.lib.uchicago.edu/ochre?uuid=fcf87b74-93b6-4dc2-a005-2a94d9a1bd6e",
        12: "http://ochre.lib.uchicago.edu/ochre?uuid=770214c7-0111-4081-a7bf-c2fa91a835ab",
        13: "http://ochre.lib.uchicago.edu/ochre?uuid=a71f2951-2927-41d3-b642-0f1c8889e75c",
        14: "http://ochre.lib.uchicago.edu/ochre?uuid=afa123cd-e3cb-4de0-ac72-a2d89b6cd0a2",
        15: "http://ochre.lib.uchicago.edu/ochre?uuid=560f9b90-8024-475c-9755-8455def7d7d4",
        16: "http://ochre.lib.uchicago.edu/ochre?uuid=55409229-ac80-46a8-a7a3-f804d6e157d4",
        17: "http://ochre.lib.uchicago.edu/ochre?uuid=7a6979b4-abd8-4722-a76d-fe8e83b77464",
        18: "http://ochre.lib.uchicago.edu/ochre?uuid=7f4a601b-4197-4013-886d-633a2e8d6ba6"
    }
'''
