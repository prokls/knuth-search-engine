#!/usr/bin/env python

"""
    knuth
    =====

    A document repository with browsing, storage and indexing capabilities.

    (C) 10.12.25, 2013, Lukas Prokop, Andi
"""

from flask import Flask
from flask import render_template
from flask import request
from datetime import datetime
from flask.ext.sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:1445@localhost/knuth_db';

db = SQLAlchemy(app);

class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(20))
    title = db.Column(db.String(256))
    author = db.Column(db.String(40))
    timestamp = db.Column(db.Integer)
    parent = db.Column(db.Integer)

    def __init__(self):
        print 'Document:' % (self.id)
        
    def __repr__(self):
        return self.title

    def getDate(self):
        return datetime.utcfromtimestamp(self.timestamp)

class Metadata(db.Model):
    __tablename__ = "metadata"
    id = db.Column(db.Integer, primary_key = True)
    document = db.Column(db.Integer)
    key = db.Column(db.String(40))
    value = db.Column(db.Text)

    def __init__(self):
        print 'Metadata:' % (self.id)
        
    def __repr__(self):
        return self.key



@app.route('/faq')
def faq():
    return render_template('faq.html')


@app.route('/impressum')
def impressum():
    return render_template('impressum.html')


@app.route('/syntax')
def info():
    return render_template('syntax.html')


@app.route('/create')
def create(methods=['GET', 'POST']):
    return render_template('create.html')


@app.route('/browse')
@app.route('/list/<int:page>')
def list(page=0, methods=['GET']):
    # 1. request data from DB
    documents = Document.query.all()
    
    document_dict = {}
    for doc in documents:
        document_dict[str(doc.id)] = doc
        
    # 2. provide data to template engine
    return render_template('list.html', **{'documents' : document_dict})


@app.route('/update')
def update(methods=['POST', 'PUT']):
    return render_template('doc.html')


@app.route('/delete/<int:doc_id>')
def delete(doc_id, methods=['DELETE']):
    return render_template('doc.html', doc_id=doc_id)


@app.route('/doc/<int:doc_id>')
def doc(doc_id):
    document = Document.query.filter_by(id=doc_id).first()
    metadata = Metadata.query.filter_by(document=doc_id).all()
    
    return render_template('doc.html', **{'document' : document, 'metadata' : metadata})


@app.route('/')
@app.route('/search')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    # TODO: change to debug=False for production
    app.run(debug=True, port=5000)
