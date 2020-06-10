# Using OCHRE as the backend for Learning Yucatec Maya

John Jung, Senior Programmer/Analyst, The University of Chicago Library

These notes are about using OCHRE as a website backend for the [Learning Yucatec Maya website](https://lucy.lib.uchicago.edu/) at the University of Chicago. OCHRE is the Online Cultural and Historical Research Environment; produced by [OCHRE Data Services](https://oi.uchicago.edu/research/ochre-data-service) at the Oriental Institute, it is software to "record, integrate, analyze, publish, and preserve cultural and historical information in all of its digital forms." 

OCHRE provides an interface to manage complex semi-structured data for cultural heritage and historical research. Because of the richness of this kind of data, this software can be helpful as a website backend, since so much development time for a site like this can go towards data management issues. By providing an API that exposes its data as XML, OCHRE can serve as a backend for website frontends written in whatever language and framework you like. 

The Learning Yucatec Maya site a web-based course to teach field researchers Yucatec Maya. It contains digitized sound clips from field recordings of native speakers that date back to the 1920's. That content is divided among 18 lessons which take the learner through a series of drills, quizzes, vocabulary lists, conversation prompts and more. 

1. [A short history of this project](#a-short-history-of-this-project)
2. [Getting started with OCHRE data](#getting-started-with-ochre-data)
3. [Creating a Flask app for OCHRE](#creating-a-flask-app-for-ochre)

## A short history of this project
The recordings themselves are valuable documents. Manuel J. Andrade was an anthropologist and linguist who did innovative audio recordings for linguistic fieldwork on the Mayan languages of Mexico and Guatemala. He recorded many of the earliest clips that are represented in today's site. Norman A. McQuown joined the faculty of the university in 1946, and he worked to conserve these recordings. When he co-founded the Language Laboratories and Archives in 1954 he incorporated these recordings into that collection. He developed courses on language instruction based on these materials, which led to "historically deep, regionally broad, and ethnographically contextualized collections of recordings, papers, and pedagogical materials."

Fast-forwarding to 2005 brings us to the initial website for this project, when Professors John Lucy and John Goldsmith led a project to digitize this material and to develop metadata to describe them. In 2007 John Lucy led a project to create the initial web-based language instruction course based on this material which is now used by multiple universities. 

### This iteration of the site
Last year OCHRE data services loaded the sound clips and their associated metadata into OCHRE. My task was to duplicate the 2007 website but with a more modern web framework. Because OCHRE reveals its data as XML, you have lots of choices for languages and frameworks for a frontend. I chose the Python language and the Flask framework because it is lightweight and quick for development&mdash;the [Flask documentation](https://flask.palletsprojects.com/en/1.1.x/) includes a tutorial about the framework itself which will be helpful if you're just getting started using it. The following instructions were tested on a Mac&mdash;if you're working with a different OS you will have to modify them for your machine.

## Getting started with OCHRE data
Next let's start to work with OCHRE. Data is organized in OCHRE by uuid&mdash;you'll need to refer to the OCHRE backend to get a UUID to start with, but since I know one already you can use the following command in the terminal to see what data is associated with it:

```console
$ curl "http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5" | xmllint --format - | less
```

This returns all of the exercises for lesson one of the Learning Yucatec Maya site&mdash;basic sentences, pronunciation, grammar, drills, listening in, conversation, vocabulary, etc.  

### Using Safari as a quick tool to explore XML data
If you haven't worked much with XML data you will probably want to start building a suite of tools that are appropriate for different tasks, like [Oxygen](https://oxygenxml.com) for making edits, or [xmllint](http://xmlsoft.org/xmllint.html) for validating and manipulating XML on the command line.

A fast way to start exploring XML data is to use a web browser that can format it with expandable and collapsible sections. On my mac I can open [http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5](http://ochre.lib.uchicago.edu/ochre?uuid=0ad43a89-09d6-4292-88cb-b6fd6dfe41e5) in Safari to do this. Control-click anywhere in the page and select "Show Page Source". The web inspector will appear- be sure you're on the Sources tab, and click the root element&mdash;Response, in this case. Select the DOM Tree option to get an easy to navigate view of this XML document. Click the `<xq:result>` element to open that part of the DOM tree, and then click `<ochre>`, `<text>`, and finally `<discourseHierarchy>`. There we can see a `<section>` for each sentence in Basic Sentences. Clicking the first `<section>` element reveals `<transcription>` and `<translation>` elements. If you open up `<translation>` you can see a `<content>` element that includes the text "Hi there, brother!" This is the first sentence of this part of lesson one.
    
### A terminal script for OCHRE data
Now we'll write a short command line script to display the dialog for lesson one's basic sentences. First, we'll need to figure out an [XPath](https://www.w3.org/TR/1999/REC-xpath-19991116/) that can get us to this part of the document. Looking at the hierarchy in Safari, I can see that we followed this trail of elements like this to get to our list of sections:

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

There are lots of different XML packages in Python&mdash;to keep things simple I'll use [ElementTree](https://docs.python.org/3/library/xml.etree.elementtree.html). It uses a subset of XPath, so I'll write some expressions a bit differently than I would with other processors. Because ElementTree works from the root element, we'll modify that XPath so that it's relative to the root. 

```xpath
./xq:result/ochre/text/discourseHierarchy/section
```

To write our command line script, I'll set up a Python virtual environment for any modules we'll need, and I'll start by installing requests to request our OCHRE data over http. I used Python 3 for these examples, so I'll start by using (Homebrew)[https://brew.sh] to install Python3.8.

```console
$ brew install python@3.8
$ alias python=/usr/local/opt/python@3.8/bin/python3
$ python -m venv env
$ source env/bin/activate
```

You may need to modify the steps above for something more appropriate for your system. In any case, what we want to do is to install Python3 via Homebrew, and set it up so that you can easily run that version of Python instead of one of the others that is probably installed on your system. Now lets put those pieces together. Here is how to iterate over each section element in that data in Python. I'll call this example hello.py:

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
In the script above, I use the Python `urllib` module to request data from OCHRE&mdash;it's one way to request a URL, the way you might do it with a web browser or with the `curl` command in the terminal. That function returns a string which I use to instantiate an `ElementTree` object so I can manipulate the XML. Then I loop over `<section>` elements in that XML using the ElementTree's `findall` method. This is just a skeleton we can expand once we're sure that we can get at our data, and that our XPath is correct, etc.  

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
...
```

Next, we'll want to get the speaker names, transcriptions, and translations. This will let us look at more of the data, to be sure we're able to extract it from the XML without any trouble. Modify your script like this:

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
            print('{:>15}{}\n{:>15}{}\n{:>15}{}\n'.format(
                'Speaker: ',  
                section.find(
                    './/property/label[@uuid="9dc5fbbe-b8db-417f-b9d4-68efa3576e80"]/../value'
                ).text,
                'Transcription: ',
                section.find('./transcription/content').text,
                'Translation: ',
                section.find('./translation/content').text
            ))  
        except AttributeError:
            pass

if __name__=='__main__':
    main()
```

The main difference in the script above is that I used Python's string formatting method to get nicely formatted output in the terminal. Running this script you should see:

```console
$ python hello.py 
      Speaker: Pedro
Transcription: ¡Hola, sukuʾun!
  Translation: Hi there, brother!

      Speaker: Pedro
Transcription: Baʾax ka waʾalik teech.
  Translation: What do you say?

      Speaker: Marcelino
Transcription: Mix baʾal.
  Translation: Nothing!

      Speaker: Marcelino
Transcription: Kux teech. Bix a beel.
  Translation: And you, how are you?

      Speaker: Pedro
Transcription: Chéen beyaʾ.
  Translation: So-so.

      Speaker: Pedro
Transcription: ¡Jach kiʾimak in wóol in wilikech!
  Translation: Iʾm very happy to see you!

      Speaker: Marcelino
Transcription: Bey xan teen.
  Translation: Me, too.
...
```

## Creating a Flask app for OCHRE
Now let's create a simple flask app to serve this content up in a web server. Start by using pip to install the flask package into your virtual environment:

```console
$ pip install flask
```

Then, copy the following Python code into a new file to create a minimal flask app. I'll call that file lucy.py:

```python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello from Flask.'

if __name__=='__main__':
    app.run()
```

In just a few lines of code, Flask routes a url (in this case, '/') to a specific function. In this case all our function does is return a short greeting. Now run a development version of your new Flask app like this:

```console
$ python lucy.py
```

Flask's development server will then start serving your Flask site at [http://localhost:5000/](http://localhost:5000/). Flask will warn you that it's running a server meant for development only&mdash;you'll want to set up something more robust for a production environment. But for now, open this URL in your browser to see a plain text message, "Hello from Flask."

### Extending our Flask app with OCHRE

Let's extend lucy.py so it can return some data about lesson one:

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
            sections.append('{:>15}{}\n{:>15}{}\n{:>15}{}\n'.format(
                'Speaker: ',  
                section.find(
                    './/property/label[@uuid="9dc5fbbe-b8db-417f-b9d4-68efa3576e80"]/../value'
                ).text,
                'Transcription: ',
                section.find('./transcription/content').text,
                'Translation: ',
                section.find('./translation/content').text
            ))   
        except AttributeError:
            pass

    return ''.join(sections)

if __name__=='__main__':
    app.run(host="0.0.0.0", port=5000)
```

Use the built-in development server to see what this looks like:

```console
$ python lucy.py
```

This should return the correct text to your browser, but without the right newlines or anything like that. If you view the source of the page you'll see the correctly formatted text&mdash;but let's add templates next so that we can return something that will render properly as HTML.

### Adding templates to Flask

We'll start by making a data structure to send. Instead of joining my sections list into a single string, I'll set each item in the list to its own python dictionary with three keys&mdash;speaker, translation, and transcription. Then I'll loop over them in the  template to display them properly. 

Modify your lucy.py so it looks like this:

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

Then, create a directory called "templates" next to your lucy.py file. Inside that directory, make a file called base.html:

```html
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>base template</title>
  <link href="/css/lucy.css" rel="stylesheet" type="text/css">
</head>
<body>
  <div id="basic_sentences">
    {% for section in sections %}
      <div>{{ section.speaker }}</div>
      <div>{{ section.transcription }}</div>
      <div>{{ section.transcription }}</div>
    {% endfor %}
  </div>
</body>
</html>
```

Create a directory called `css` and inside it a file called `lucy.css`:

```css
body {
  font-family: Helvetica, sans-serif;
}
div#basic_sentences {
  display: grid;
  grid-template-columns: max-content 1fr 1fr;
  grid-column-gap: 1em;
  grid-row-gap: 1em;
}
```

Finally, create a one-line file called lucy.wsgi and put it next to lucy.py:

```python
from lucy import app as application
```

Your directory hierarchy should now look like this:

```
css
    lucy.css
lucy.py
lucy.wsgi
templates
    base.html
```

Now we'll want to switch from the built-in Flask server to something that can also serve static files like CSS. We'll use the [mod-wsgi Python package](https://pypi.org/project/mod-wsgi/) to do that. Inside your Python virtual environment, run the following commands:

```console
$ pip install mod_wsgi-httpd
$ pip install mod_wsgi
```

This will install a copy of Apache into your virtual environment, along with a handy command for running an Apache server with WSGI for your Flask app. Run your test server with the following command:

```console
$ mod_wsgi-express start-server --url-alias /css css lucy.wsgi
```

Now if you open your browser to http://localhost:8000 you'll see that the site should be correctly serving both static files and dynamic content. Please note:  I ran into some trouble running mod_wsgi-express with the default Python 3.7 on my Mac. This seems to be a common issue based on the GitHub page for that software, but using Homebrew's Python3.8 worked around that problem. 

If you go to [https://github.com/uchicago-library/lucy](https://github.com/uchicago-library/lucy) you can see production code for the site, which expands on the ideas here. Please be sure to share the projects you make with OCHRE, I'm looking forward to seeing them. 
