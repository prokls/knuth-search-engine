#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    knuth
    =====

    A document repository with browsing, storage and indexing capabilities.

    (C) 10.12.25, 2013, Lukas Prokop, Andi
"""

from flask import Flask, render_template, request, url_for
from flask import request, redirect, abort, send_from_directory

from werkzeug.contrib.atom import AtomFeed

from database import Document
from database import Metadata
from database import db

import os.path
import document
import datetime
import feedparser
import collections
import elasticsearch

FEED_TITLE = 'Newest Uploads'
FEED_NUM_DOCUMENTS = 5

es = elasticsearch.Elasticsearch()
app = Flask(__name__)
app.jinja_env.add_extension("jinja2.ext.do")
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1445@localhost/knuth_db';

db.init_app(app)


@app.route('/faq')
def faq():
    return render_template('faq.html', page='faq')


@app.route('/impressum')
def impressum():
    return render_template('impressum.html', page='impressum')


@app.route('/syntax')
def info():
    return render_template('syntax.html', page='info')


def normalize_data(form, files):
    """Take userform from upload and return normalized data"""
    try:
        doc_file = files['doc']
    except KeyError:
        doc_file = None
    try:
        attach_file = files['attach_doc']
    except KeyError:
        attach_file = None

    return {
      'op' : form['op'].lower(),
      'id' : int(form['doc_id']),
      'title' : form['doc_title'],
      'author' : form['doc_author'],
      'tags' : [tag for tag in form['doc_tags'].split() if tag],
      'doc' : doc_file,
      'attachment' : {
        'title' : form['attach_title'],
        'author' : form['attach_author'],
        'doc' : attach_file
      }
    }


def create_empty_doc():
    """Return an empty document for `create`."""
    d = collections.defaultdict(lambda: '', {'doc_id' : 0})
    return normalize_data(d, d)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new document (POST) or provide new document form."""
    if request.method == 'POST':
        data = normalize_data(request.form, request.files)

        if data['id'] == 0:
            doc_id = document.create_document(data['title'], \
              data['author'], data['tags'])
        else:
            d = {}
            whitelist = ['id', 'title', 'author']
            for key in whitelist:
                if data[key]:
                    d[key] = data[key]
            document.update_document(data['id'], **d)
            doc_id = data['id']

        if data['doc']:
            filename = document.upload_doc(data['doc'], doc_id)
        else:
            filename = document.get_filename(doc_id)

        # tags get inherited
        if data['attachment']['doc']:
            at = document.create_attachment(doc_id,
                    data['attachment']['title'],
                    data['attachment']['author'], data['tags'])
            attach = document.upload_doc(data['attachment']['doc'], at)

        doc = document.retrieve_document(doc_id)
    else:
        # create empty document
        doc = create_empty_doc()

    op = request.form.get('op')

    if not op or op == u'Attach':
        return render_template('create.html', **doc)
    else:
        return redirect(url_for('doc', doc_id=doc['id']))


@app.route('/browse')
@app.route('/list/', defaults={'page' : 0})
@app.route('/list/<int:page>')
def list(page=0):
    # 1. request data from DB
    documents = Document.query.all()
    
    document_dict = {}
    for doc in documents:
        document_dict[str(doc.id)] = doc
        
    # 2. provide data to template engine
    return render_template('list.html', **{'documents' : document_dict, 'page' : 'list'})


@app.route('/update', methods=['POST', 'PUT'])
def update():
    return render_template('doc.html', page='update')


@app.route('/delete/<int:doc_id>')
def delete(doc_id, methods=['DELETE']):
    return render_template('doc.html', doc_id=doc_id, page='delete')


def make_feed_body(doc):
    feed_body = u'Title: ' + doc.title + \
                 '<br />Author: ' + doc.author + \
                 '<br />Upload: ' + doc.getFormatDateString()
    return feed_body

def create_feed():
    feed = AtomFeed(FEED_TITLE, feed_url=request.url, url=request.url_root)
    newest_documents = Document.query.order_by(Document.timestamp.desc()) \
        .limit(FEED_NUM_DOCUMENTS).all()
    
    for doc in newest_documents:
        feed.add(doc.title or u'(no title given)',
                 make_feed_body(doc),
                 content_type='html',
                 url=url_for('doc', doc_id=doc.id),
                 updated=doc.getDate())
    
    return feed

@app.route('/feed')
def feed():
    feed = create_feed()
    return feed.get_response()

@app.route('/news')
def news():
    feed_str = create_feed().to_string()
    parsed_feed = feedparser.parse(feed_str)

    for entry in parsed_feed['entries']:
        dt = datetime.datetime.strptime(entry['updated'], '%Y-%m-%dT%H:%M:%SZ')
        entry['updated'] = dt.strftime('%Y-%m-%d %H:%M')

    return render_template('news.html', **{'feed' : parsed_feed})


@app.route('/doc/<int:doc_id>')
def doc(doc_id):
    docu = document.retrieve_document(doc_id)
    if not docu:
        abort(404)
    
    return render_template('doc.html', **docu)


@app.route('/data/<filename>')
def download(filename):
    return send_from_directory(document.UPLOAD_FOLDER, filename)



@app.route('/')
@app.route('/search')
def main():
    query = request.args.get('q')
    if query:
        search_query = {'query': {'query_string': {'query': query}}}
        print(es.search(doc_type='doc', size=50, index='knuth', q=query))
        # TODO: in which structure are the results returned? supply it to listresults!

        return 
    return render_template('listresults.html', page='listresults')


if __name__ == '__main__':
    # TODO: change to debug=False for production
    app.run(debug=True, port=5000)
