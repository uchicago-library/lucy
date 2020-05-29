# Using OCHRE as the backend for Learning Yucatec Maya
These notes are about using OCHRE as a website backend for the [Learning Yucatec Maya website](https://lucy.lib.uchicago.edu/) at the University of Chicago. OCHRE is the Online Cultural and Historical Research Environment; produced by [OCHRE Data Services](https://oi.uchicago.edu/research/ochre-data-service) at the Oriental Institute, it is software to "record, integrate, analyze, publish, and preserve cultural and historical information in all of its digital forms." 

OCHRE provides an interface to manage complex semi-structured data for cultural heritage and historical research. Because of the richness of this kind of data, this software can be helpful as a website backend, since so much development time for a site like this can go towards data management issues. By providing an API that exposes its data as XML, OCHRE can serve as a backend for website frontends written in whatever language and framework you like. 

The Learning Yucatec Maya site a web-based course to teach field researchers Yucatec Maya. It contains digitized sound clips from field recordings of native speakers that date back to the 1920's. That content is divided among 18 lessons which take the learner through a series of drills, quizzes, vocabulary lists, conversation prompts and more. 

## A short history of this project
The recordings themselves are valuable documents. Manuel J. Andrade was an anthropologist and linguist who did innovative audio recordings for linguistic fieldwork on the Mayan languages of Mexico and Guatemala. He recorded many of the earliest clips that are represented in today's site. Norman A. McQuown joined the faculty of the university in 1946, and he worked to conserve these recordings. When he co-founded the Language Laboratories and Archives in 1954 he incorporated these recordings into that collection. He developed courses on language instruction based on these materials, which led to "historicall deep, regionally broad, and ethnographically contextualized collections of recordings, papers, and pedagogical materials."

Fast-forwarding to 2005 brings us to the initial website for this project, when Professors John Lucy and John Goldsmith led a project to digitize this material and to develop metadata to describe them. In 2007 John Lucy led a project to create the initial web-based language instruction course based on this material which is now used by multiple universities. 

## This iteration of the site
Last year OCHRE data services loaded the sound clips and their associated metadata into OCHRE. My task was to duplicate the 2007 website, but with a more modern web framework. Because OCHRE reveals its data as XML, you have lots of choices for languages and frameworks for a frontend. I chose the Python language and the [Flask](https://flask.palletsprojects.com/en/1.1.x/) framework because it's lightweight and quick for development. The following instructions were tested on a Mac- if you're working with a different OS you will have to modify them for your machine.

## Getting started with OCHRE data
Next lets start to work with OCHRE. Data is organized in OCHRE by uuid- you'll need to refer to the OCHRE backend to get a UUID to start with, but since I know one already you can use the following command in the terminal to see what data is associated with it:

```console
$ curl http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5 | xmllint --format - | less
```

This returns all of the exercises for lesson one of the Learning Yucatec Maya site- basic sentences, pronunciation, grammar, drills, listening in, conversation, vocabulary, etc.  

## Using Safari as a quick tool to explore XML data
If you haven't worked much with XML data you will probably want to start building a suite of tools that are appropriate for different tasks, like [Oxygen](https://oxygenxml.com) for making edits, or [xmllint](http://xmlsoft.org/xmllint.html) for validating and manipulating XML on the command line.

A fast way to start exploring XML data is to use a web browser that can format it with expandable and collapsable sections. On my mac I can open [http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5](http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5) in Safari to do this. Control-click anywhere in the page and select "Show Page Source". The web inspector will appear- be sure you're on the Sources tab, and click the root element (Response, in this case.) Select the DOM Tree option to get an easy to navigate view of this XML document. Click the `<xq:result>` element to open that part of the DOM tree, and then click `<ochre>`, `<text>`, and finally `<discourseHierarchy>`. There we can see a `<section>` for each sentence in Basic Sentences. Clicking the first `<section>` element reveals `<transcription>` and `<translation>` elements. If you open up `<translation>` you can see a `<content>` element that includes the text "Hi there, brother!" This is the first sentence of this part of lesson one.
    
## Writing a script to format this data for display in the terminal
This short command line script will display the dialog for lesson one's basic sentences. First, we'll need to figure out an [XPath](https://www.w3.org/TR/1999/REC-xpath-19991116/) that can get us to this part of the document. Looking at the hierarchy in Safari, I can see that we followed this trail of elements like this to get to our list of sections:

```html
<ino:response>
  <xq:result>
    <ochre>
      <text>
        <discurseHierarchy>
          <section>
```

We can represent that in XPath as:

```xpath
/ino:response/xq:result/ochre/text/discourseHierarchy/section
```

There are lots of different XML packages in Python- to keep things simple I'll use [ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html). It uses a subset of XPath, so I'll write some expressions a bit differently than I would with other processors. Because ElementTree works from the root element, we'll modify that XPath so that it's relative to the root. 

```xpath
./xq:result/ochre/text/discourseHierarchy/section
```

To write our command line script, I'll set up a Python virtual environment  for any modules we'll need, and I'll start by installing requests to request our OCHRE data over http.

```console
$ python3 -m venv env
$ source env/bin/activate
$ pip install request
```

Now lets put those pieces together. Here is how to iterate over each section element in that data in Python:

```python
import urllib.request
import xml.etree.ElementTree as ET

def main():
    ochre_xml = ET.ElementTree(
        file=urllib.request.urlopen(
            'http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5'
        )   
    )   

    for section in ochre_xml.findall('./xq:result/ochre/text/discourseHierarchy/section', {
        'xq': 'http://namespaces.softwareag.com/tamino/XQuery/result'
    }): 
        print(section)

if __name__=='__main__':
    main()
```

Running this script, you should see something like this:

```
$ python hello.py
<Element 'section' at 0x10338aad0>
<Element 'section' at 0x10338fd70>
<Element 'section' at 0x103396dd0>
<Element 'section' at 0x10339f6b0>
<Element 'section' at 0x103d4c170>
<Element 'section' at 0x103d525f0>
<Element 'section' at 0x103d61a10>
<Element 'section' at 0x103d67dd0>
(output truncated)
```

Next, we'll want to get the speaker names, transcriptions, and translations. For the time being I'll format them to look something like a screenplay, just for fun. Once we've got this running on a web server we can add static content like CSS for better styling. Extend your script like this:

```python
import urllib.request
import xml.etree.ElementTree as ET

def main():
    ochre_xml = ET.ElementTree(
        file=urllib.request.urlopen(
            'http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5'
        )   
    )   

    for section in ochre_xml.findall('./xq:result/ochre/text/discourseHierarchy/section', {
        'xq': 'http://namespaces.softwareag.com/tamino/XQuery/result'
    }): 
        try:
            speaker = section.find(
                './/property/label[@uuid="9dc5fbbe-b8db-417f-b9d4-68efa3576e80"]/../value'
            ).text
            translation = section.find('./translation/content').text
            transcription = section.find('./transcription/content').text

            print('{:<35}{}\n{:<23}{} ({})\n'.format(
                '', 
                speaker.upper(),
                '', 
                transcription,
                translation
            ))  
        except AttributeError:
            pass

if __name__=='__main__':
    main()
```

Running this script you should see...

```console
$ python hello.py 
                                   PEDRO
                       ¡Hola, sukuʾun! (Hi there, brother!)

                                   PEDRO
                       Baʾax ka waʾalik teech. (What do you say?)

                                   MARCELINO
                       Mix baʾal. (Nothing!)

                                   MARCELINO
                       Kux teech. Bix a beel. (And you, how are you?)

                                   PEDRO
                       Chéen beyaʾ. (So-so.)
```

## Creating a minimal Flask app
Now lets create a simple flask app to serve this content up in a web server. Start by using pip to install the flask package into your virtual environment:

```console
$ pip install flask
```

Then, copy the following Python code into a new file to create a minimal flask app. I'll call that file minimal.py:

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Flask.'

if __name__=='__main__':
    app.run()
```

Now run a development version of your new Flask app like this:

```console
$ python minimal.py
```

Flask's development server will then start serving your Flask site on localhost at (http://localhost:5000/)[http://localhost:5000/]. Flask will warn you that it's running a server meant for development only- later on we'll set up a simple WGSI server so you can get a bit closer to what this will look like in  a production environment. Opening this URL in your browser should show a plain text message, "Hello from Flask."

Lets extend that so it can return our screenplay-formatted text.

```python
import urllib.request
import xml.etree.ElementTree as ET

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    ochre_xml = ET.ElementTree(
        file=urllib.request.urlopen(
            'http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5'
        )   
    )   

    sections = []

    for section in ochre_xml.findall('./xq:result/ochre/text/discourseHierarchy/section', {
        'xq': 'http://namespaces.softwareag.com/tamino/XQuery/result'
    }): 
        try:
            speaker = section.find(
                './/property/label[@uuid="9dc5fbbe-b8db-417f-b9d4-68efa3576e80"]/../value'
            ).text
            translation = section.find('./translation/content').text
            transcription = section.find('./transcription/content').text

            sections.append('{:<35}{}\n{:<23}{} ({})\n'.format(
                '', 
                speaker.upper(),
                '', 
                transcription,
                translation
            ))  
        except AttributeError:
            pass

    return ''.join(sections)

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)
```

This should return the correct text to your browser, but without the right newlines or anything like that. Lets add templates so that we can return something more nicely formatted. 

Finally, lets add templates to return this as HTML. Instead of sending a mass of text to the templates, we'll start by making a data structure to send. Instead of joining my sections list into a single string, I'll set each item in the list to it's own python dictionary with three keys- speaker, translation, and transcription. Then I'll loop over them in the  template to display them properly. 

Modify your main.py so it looks like this:

```python
import urllib.request
import xml.etree.ElementTree as ET

from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def main():
    ochre_xml = ET.ElementTree(
        file=urllib.request.urlopen(
            'http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5'
        )   
    )   

    sections = []

    for section in ochre_xml.findall('./xq:result/ochre/text/discourseHierarchy/section', {
        'xq': 'http://namespaces.softwareag.com/tamino/XQuery/result'
    }): 
        try:
            sections.append({
                'speaker': section.find(
                    './/property/label[@uuid="9dc5fbbe-b8db-417f-b9d4-68efa3576e80"]/../value'
                ).text,
                'translation': section.find('./translation/content').text,
                'transcription': section.find('./transcription/content').text
            })  
        except AttributeError:
            pass

    return render_template(
        'base.html',
         sections=sections
    )

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)
```

Then, create a directory called "templates" next to your main.py file. Inside that directory, make a file called base.html:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>base template</title>
  <style>
    body {
      font-family: courier, monospace;
    }   
    h2 {
      font-size: 12pt;
      font-weight: normal;
      margin: 0 0 0 4in;
      text-transform: uppercase;
    }   
    p { 
      font-size: 12pt;
      margin: 0 0 12pt 2.5in;
    }   
  </style>
</head>
<body>
{% for section in sections %}
    <h2>{{ section.speaker }}</h2>
    <p>{{ section.transcription }} ({{ section.transcription }})</p>
{% endfor %}
</body>
</html>
```

Now if you run main.py, you should see something that looks vaguely like a screenplay, at least on a desktop browser. 

# Docker?

In order to serve static files it's probably best to set up a better development environment. We'll use Docker. Go to [the Docker website](https://docs.docker.com/get-docker/) to download a version that's appropriate for your computer. 

Create a directory called "app", and move hello.py and the css and templates directories inside. Then create a file called Dockerfile next to the app directory, with the following contents:

```
#UPDATE THIS LINE
FROM tiangolo/uwsgi-nginx-flask:flask

COPY ./app /app
```

Your directory heirarchy should now look like this:

```
Dockerfile
app
    css
        base.css
    index.py
    templates
        base.html
env
    (virtual environment stuff)
```

Start the docker daemon, and build the project with the following command:

```console
$ docker build -t hello .
$ docker run -p 80:80 -t hello
```

Now if you open your browser to http://localhost:5000 you'll be able to see it with the correct fonts. 

If you go to https://github.com/johnjung/lucy you can see production code for the site, extending the ideas here. 
