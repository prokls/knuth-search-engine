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

app = Flask(__name__)


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
    # 2. provide data to template engine
    return render_template('list.html', **{'documents' : []})


@app.route('/update')
def update(methods=['POST', 'PUT']):
    return render_template('doc.html')


@app.route('/delete/<int:doc_id>')
def delete(doc_id):
    return render_template('doc.html', doc_id=doc_id)


@app.route('/doc/<int:doc_id>')
def doc(doc_id, methods=['DELETE']):
    return render_template('doc.html')


@app.route('/')
@app.route('/search')
def main():
    return render_template('index.html')


if __name__ == '__main__':
    # TODO: change to debug=False for production
    app.run(debug=True, port=5000)
