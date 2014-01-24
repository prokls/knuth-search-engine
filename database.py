#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    knuth.database
    ~~~~~~~~~~~~~~

    Database interaction for the knuth search engine.

    (C) 10.12.25, 2013, 2014, Lukas Prokop, Andi
"""

from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime
import time

db = SQLAlchemy()


class Document(db.Model):
    """A document like papers, theses, ..."""
    __tablename__ = "documents"

    # table columns
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    type = db.Column(db.String(20))
    title = db.Column(db.String(256))
    author = db.Column(db.String(40))
    doi = db.Column(db.String(256))
    timestamp = db.Column(db.Integer)
    parent = db.Column(db.Integer)

    def __init__(self, type='doc', title='', author='',
                 doi='', timestamp=None, parent=None):
        if not timestamp:
            timestamp = int(time.time())

        self.type = type
        self.title = title
        self.author = author
        self.doi = doi
        self.timestamp = timestamp
        self.parent = parent

    def __repr__(self):
        return 'Document({})'.format(self.title)

    def get_date(self):
        if self.timestamp == 0:
            return None
        return datetime.utcfromtimestamp(self.timestamp)

    def get_format_date_string(self):
        dt = self.get_date()
        if dt:
            return dt.strftime('%Y-%m-%d')
        else:
            return ''


class Metadata(db.Model):
    """Table for metadata of a document"""
    __tablename__ = "metadata"

    # table columns
    document = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(40), primary_key=True)
    value = db.Column(db.Text, primary_key=True)

    def __init__(self, document, key, value=''):
        self.document = document
        self.key = key
        self.value = value

    def __repr__(self):
        return self.key
