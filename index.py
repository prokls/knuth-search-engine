#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    knuth
    ~~~~~

    A document repository with browsing, storage and indexing capabilities.

    (C) 10.12.25, 2013, 2014, Lukas Prokop, Andi
"""

# imports
from flask import Flask, render_template, request, url_for
from flask import request, redirect, abort, send_from_directory

from werkzeug.contrib.atom import AtomFeed

from database import Document
from database import db

import os.path
import document
import datetime
import feedparser
import collections
import elasticsearch

# setup
FEED_TITLE = 'Newest Uploads'
FEED_NUM_DOCUMENTS = 5

es = elasticsearch.Elasticsearch()
app = Flask(__name__)
app.jinja_env.add_extension('jinja2.ext.do')
DB_URI = u'postgresql://postgres:1445@localhost/knuth_db'
app.config['SQLALCHEMY_DATABASE_URI'] = DB_URI

db.init_app(app)

FEED_BODY = u'''Title: {:title}<br />
Author: {:author}<br />
DOI: {:doi}<br />
Upload: {:upload}'''


# routing
@app.route('/faq')
def faq():
    """Frequently Asked Questions page"""
    return render_template('faq.html', page='faq')


@app.route('/impressum')
def impressum():
    """Impressum page"""
    return render_template('impressum.html', page='impressum')


@app.route('/syntax')
def info():
    """Information about the search engine syntax"""
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
      'op': form['op'].lower(),
      'id': int(form['doc_id']),
      'title': form['doc_title'],
      'author': form['doc_author'],
      'doi': form['doc_doi'],
      'tags': [tag for tag in form['doc_tags'].split() if tag],
      'doc': doc_file,
      'attachment': {
        'title': form['attach_title'],
        'author': form['attach_author'],
        'doi': '',
        'doc': attach_file
      }
    }


def create_empty_doc():
    """Return an empty document for `create`."""
    d = collections.defaultdict(lambda: '', {'doc_id': 0})
    return normalize_data(d, d)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """Create a new document (POST) or provide new document form."""
    if request.method == 'POST':
        data = normalize_data(request.form, request.files)

        if data['id'] == 0:
            doc_id = document.create_document(data['title'],
              data['author'], data['doi'], data['tags'])
        else:
            d = {}
            whitelist = ['id', 'title', 'author', 'doi']
            for key in whitelist:
                if data[key]:
                    d[key] = data[key]
            document.update_document(data['id'], **d)
            doc_id = data['id']

        if data['doc']:
            filename = document.upload_doc(es, data['doc'], doc_id)
        else:
            filename = document.get_filename(doc_id)

        # tags get inherited
        if data['attachment']['doc']:
            at = document.create_attachment(doc_id,
                    data['attachment']['title'],
                    data['attachment']['author'],
                    data['attachment']['doi'],
                    data['tags'])
            attach = document.upload_doc(es, data['attachment']['doc'], at)

        docu = document.retrieve_document(doc_id)
    else:
        # create empty document
        docu = create_empty_doc()

    op = request.form.get('op')

    if not op or op == u'Attach':
        return render_template('create.html', **docu)
    else:
        document.index_document_by_id(es, docu['id'])
        return redirect(url_for('doc', doc_id=docu['id']))


@app.route('/browse')
@app.route('/list')
def listing(page=0):
    """Create a list of all available documents"""
    # 1. request data from DB
    documents = Document.query.filter(Document.parent is None).all()
    attachments = Document.query.filter(Document.parent is not None).all()

    document_dict = {}
    for doc in documents:
        document_dict[str(doc.id)] = {'document': doc, 'attachments': []}

    for attachment in attachments:
        doc_dict_entry = document_dict[str(attachment.parent)]
        print doc_dict_entry
        doc_dict_entry['attachments'].append(attachment)

    # 2. provide data to template engine
    return render_template('list.html',
        **{'documents': document_dict, 'page': 'listing'}
    )


@app.route('/update', methods=['POST', 'PUT'])
def update():
    """Update a document"""
    return render_template('doc.html', page='update')


@app.route('/delete/<int:doc_id>')
def delete(doc_id, methods=['DELETE']):
    """Delete a document"""
    document.delete_document(doc_id)
    return redirect(url_for('main'))


def make_feed_body(doc):
    """Create the body text of a feed entry"""
    doi = ''
    if doc.doi is not None:
        doi = doc.doi

    return FEED_BODY.format(title=doc.title, author=doc.author,
        doi=doi, upload=doc.get_format_date_string()
    )


def create_feed():
    """Create an AtomFeed instance with latest documents"""
    feed = AtomFeed(FEED_TITLE, feed_url=request.url, url=request.url_root)
    newest_documents = Document.query.order_by(Document.timestamp.desc()) \
        .limit(FEED_NUM_DOCUMENTS).all()

    for doc in newest_documents:
        feed.add(doc.title or u'(no title given)',
                 make_feed_body(doc),
                 content_type='html',
                 url=url_for('doc', doc_id=doc.id),
                 updated=doc.get_date())

    return feed


@app.route('/feed')
def feed():
    """Return a AtomFeed for the latest uploaded documents"""
    feed = create_feed()
    return feed.get_response()


@app.route('/news')
def news():
    """Page listing latest documents"""
    feed_str = create_feed().to_string()
    parsed_feed = feedparser.parse(feed_str)

    for entry in parsed_feed['entries']:
        dt = datetime.datetime.strptime(entry['updated'], '%Y-%m-%dT%H:%M:%SZ')
        entry['updated'] = dt.strftime('%Y-%m-%d %H:%M')

    return render_template('news.html', **{'feed': parsed_feed})


@app.route('/doc/<int:doc_id>')
def doc(doc_id):
    """Presentation of a single document"""
    docu = document.retrieve_document(doc_id)
    if not docu:
        abort(404)

    return render_template('doc.html', **docu)


@app.route('/data/<filename>')
def download(filename):
    """Download a file from the repository"""
    filename = os.path.basename(filename)
    return send_from_directory(document.UPLOAD_FOLDER, filename)


@app.route('/')
@app.route('/search')
def main():
    """Main routine"""
    query = request.args.get('q')
    results = {}

    if query:
        # if some query is specified, search
        search_query = {'query': {'query_string': {'query': query}}}
        es_params = {'index': 'knuth', 'doc_type': 'document',
                     'size': 50, 'body': search_query}
        search_result = es.search(**es_params)
        hits = search_result['hits']['hits']

        for hit in hits:
            document_id = hit['_id']
            d = Document.query.filter_by(id=document_id).first()
            results[str(document_id)] = d

    print results

    tmpl_params = {'results': results, 'page': 'listresults'}
    return render_template('listresults.html', **tmpl_params)


if __name__ == '__main__':
    # TODO: change to debug=False for production
    app.run(debug=True, port=5000)
