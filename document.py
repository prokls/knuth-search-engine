#!/usr/bin/env python

"""
    knuth.document
    ~~~~~~~~~~~~~~

    Document handling in knuth document repository.

    (C) 2014, Lukas Prokop, Andi
"""

from database import db, Document, Metadata

import os.path
import datetime
import pdfminer
import mimetypes

UPLOAD_FOLDER = 'data'

DOC_COLUMNS = ['id', 'type', 'timestamp', 'author', 'timestamp', 'parent']
METADATA_COLUMNS = ['document', 'key', 'value']

attach1 = {'id': 1, 'type': 'attach', 'timestamp': 1330073752,
  'author': 'Andreas Schulhofer', 'title': 'An improvement',
  'filename': '1.pdf', 'parent': None, 'tags': ['cs']}
attach2 = {'id': 42, 'type': 'attach', 'timestamp': 1290023752,
  'author': 'Bernd', 'title': 'Code review', 'filename': '42.pdf',
  'parent': None, 'tags': ['cs']}


def create_document(title='', author='', tags=[], **kwargs):
    """Define a new document in the database. Returns new ID."""
    # create new document
    new_doc = Document(kwargs.get('type', 'doc'), title, author, \
                       None, kwargs.get('parent'))
    db.session.add(new_doc)
    db.session.commit()  # retrieve new_doc.id

    # create new tags
    for tag in tags:
        if tag:
            new_tag = Metadata(new_doc.id, 'tag', tag.strip())
    db.session.commit()

    return new_doc.id


def retrieve_document(doc_id, with_attachments=True):
    """Retrieve document and all associated information using `doc_id`.
    Does not return attachments of attachment. Returns dict.
    """
    doc = Document.query.filter_by(id=doc_id).first()
    metadata = Metadata.query.filter_by(document=doc_id).all()
    data = {'tags' : [], 'attachments' : []}
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
            data[entry.key] = entry.value

    # retrieve children
    children = Document.query.filter_by(parent=doc_id).all()
    for child in children:
        data['attachments'].append(
            document.retrieve_document(child.id, with_attachments=False)
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


def upload_doc(filepath, doc_id):
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
    print('File {} stored.'.format(new_filename))

    # store metadata entry: document=doc_id key='filename' value=file_path
    filename_row = Metadata(doc_id, 'filename', new_filename)
    db.session.add(filename_row)

    # store metadata entry: document=doc_id key='mimetype' value=mimetype
    if mimetype:
        mimetype_row = Metadata(doc_id, 'mimetype', mimetype)
        db.session.add(mimetype_row)

    # TODO: retrieve metadata using pdfminer, if PDF
    # TODO: add content to search engine, if plain text
    # TODO: add metadata to search engine

    db.session.commit()

    return '42.pdf'
