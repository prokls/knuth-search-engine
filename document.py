#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    knuth.document
    ~~~~~~~~~~~~~~

    Document handling in knuth document repository.

    (C) 2014, Lukas Prokop, Andi
"""

from database import db, Document, Metadata

import os.path
import datetime
import mimetypes

import pdfminer
import pdfminer.pdfparser
import pdfminer.pdfdocument

UPLOAD_FOLDER = 'data'

DOC_COLUMNS = ['id', 'type', 'title', 'author', 'timestamp', 'parent']
METADATA_COLUMNS = ['document', 'key', 'value']


def create_document(title='', author='', tags=[], **kwargs):
    """Define a new document in the database. Returns new ID."""
    # create new document
    new_doc = Document(kwargs.get(u'type', u'doc'), title, author, \
                       None, kwargs.get(u'parent'))
    db.session.add(new_doc)
    db.session.commit()  # retrieve new_doc.id

    # create new tags
    for tag in tags:
        if tag:
            new_tag = Metadata(new_doc.id, u'tag', tag.strip())
            db.session.add(new_tag)

    db.session.commit()
    return new_doc.id


def retrieve_document(doc_id, with_attachments=True):
    """Retrieve document and all associated information using `doc_id`.
    Does not return attachments of attachment. Returns dict.
    """
    doc = Document.query.filter_by(id=doc_id).first()
    metadata = Metadata.query.filter_by(document=doc_id).all()
    data = {'tags' : [], 'attachments' : [], 'meta': {}}
    children = set([])

    # retrieve document data
    for field in DOC_COLUMNS:
        data[field] = getattr(doc, field)
    data['id'] = int(data['id'])

    # retrieve metadata
    for entry in metadata:
        if entry.key == 'tag':
            data['tags'].append(entry.value)
            continue
        if not data.has_key(entry.key):
            data['meta'][entry.key] = entry.value

    # retrieve children
    if with_attachments:
        children = Document.query.filter_by(parent=doc_id).all()
        for child in children:
            data['attachments'].append(
                retrieve_document(child.id, with_attachments=False)
            )

    data['filename'] = get_filename(doc_id)

    return data


def update_document(doc_id, **attributes):
    """Update document data with updated attributes. Returns None."""
    doc = Document.query.filter_by(id=doc_id).first()
    if doc:
        for attr, attr_value in attributes.iteritems():
            setattr(doc, attr, attr_value)
        db.session.commit()
        return doc_id


def delete_document(doc_id):
    """Delete a document by its `doc_id`. Returns None."""
    if int(doc_id) == 0:
        print('Cannot delete document with ID 0.')
        return

    docs = set([])
    tmp = set([doc_id])

    # Retrieve set of documents related to document `doc_id` in hierarchy
    # ... and delete them already from the Document table
    # Using Breadth-First Search.
    while tmp:
        current = tmp.pop()
        results = Document.query.filter_by(parent=current).all()
        for result in results:
            tmp.add(result.id)
            db.session.delete(result)  # delete document
        docs.add(current)
    db.session.delete(Document.query.filter_by(id=doc_id).first())

    # Remove any metadata related to documents with ID in `docs`
    for document_id in docs:
        mds = Metadata.query.filter_by(document=document_id).all()
        for md in mds:
            if md.key == 'filename':
                os.unlink(os.path.join(UPLOAD_FOLDER, md.value))  # delete file
            db.session.delete(md)  # delete metadata


def create_attachment(parent, title="", author="", tags=[]):
    """Create a new attachment. Returns new ID."""
    return create_document(title, author, tags, parent=parent, type='attach')


def get_filename(doc_id):
    """Retrieve the filename of document with id=`doc_id`"""
    md = Metadata.query.filter_by(key='filename').first()
    if md:
        return md.value

    for filename in os.listdir(UPLOAD_FOLDER):
        if filename.startswith(str(doc_id) + '.'):
            return filename

    return None


def _add_metadata_row(doc_id, key, value):
    """Add entry to table Metadata"""
    if key and value:
        row = Metadata(doc_id, key, value)
        db.session.add(row)


def upload_doc(es_connection, filepath, doc_id):
    """Take document from filepath and store it according to `doc_id`
    so we can retrieve it later. Also register at search engine and
    retrieve further metadata from the document. Returns new filename.
    """
    # retrieve file extension & mime type
    if '.' in filepath.filename:
        fileext = filepath.filename.rsplit('.', 1)[1]
    else:
        fileext = str(doc_id)

    try:
        mimetype = mimetypes.types_map['.' + fileext]
    except KeyError:
        mimetype = None

    new_filename = str(doc_id) + '.' + fileext
    file_path = os.path.join(UPLOAD_FOLDER, new_filename)

    # move uploaded file to repository
    filepath.save(file_path)

    # store metadata entry: document=doc_id key='filename' value=file_path
    filename_row = Metadata(doc_id, u'filename', new_filename)
    db.session.add(filename_row)

    # store metadata entry: document=doc_id key='mimetype' value=mimetype
    if mimetype:
        mimetype_row = Metadata(doc_id, u'mimetype', mimetype)
        db.session.add(mimetype_row)

    # retrieve metadata using pdfminer, if PDF
    if mimetype == 'application/pdf':
        with open(file_path, 'rb') as fp:
            parser = pdfminer.pdfparser.PDFParser(fp)
            doc = pdfminer.pdfdocument.PDFDocument(parser)
            parser.set_document(doc)
            doc.initialize()

            fields = [u'Producer', u'Creator', u'Title', u'Keywords', u'Subject']
            for key in fields:
                try:
                    keyname = u'pdf.' + key.lower()
                    try:
                        value = doc.info[0][key].decode('utf-16')
                    except UnicodeDecodeError:
                        continue
                    _add_metadata_row(doc_id, keyname, value)
                except KeyError:
                    pass

    # add content to search engine, if plain text
    if fileext in ['txt', 'tex', 'rst', 'enl']:
        with open(file_path, 'r') as fp:
            es.index(index="knuth",
                     doc_type="plaintext_document",
                     id=doc_id,
                     body=fp.read())

    # add metadata to search engine
    if es.exists(index="knuth", id=doc_id):
        docu = es.get(index="knuth", id=doc_id)
        docu['body']['filename'] = filename
        docu['body']['mimetype'] = mimetype
        docu['body']['orig_filename'] = filepath.filename
        es.update(**docu)

    db.session.commit()

    return new_filename
