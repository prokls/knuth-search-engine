#!/usr/bin/env python

"""
    knuth.document
    ~~~~~~~~~~~~~~

    Document handling in knuth document repository.

    (C) 2014, Lukas Prokop, Andi
"""

from database import db

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


def create_document(title='', author='', tags=[]):
    """Define a new document in the database. Returns new ID."""
    timestamp = int(datetime.datetime.now().strftime("%s"))
    # TODO: INSERT INTO documents with type='doc'
    # TODO: INSERT INTO metadata
    # TODO: register new tags
    return 42  # new id


def retrieve_document(doc_id):
    """Retrieve document and all associated information using `doc_id`.
    Does not return attachments of attachment. Returns dict.
    """

    return {
      'id': int(doc_id),
      'type': 'doc',
      'timestamp': 1240073752,
      'author': 'Lukas Prokop',
      'title': 'The typho typesetting system',
      'filename': str(doc_id) + '.pdf',
      'pdf.subject': 'Typho Typesetting',
      'pdf.author': 'Lukas Prokop',
      'tags': ['typesetting', 'knuth', 'tex'],
      'attachments': [attach1, attach2]
    }


def update_document(doc_id, **attributes):
    """Update document data with updated attributes. Returns None."""
    # TODO: update document
    # TODO: if key in attributes does not exist in documents, update/add entry in metadata


def delete_document(doc_id):
    """Delete a document by its `doc_id`. Returns None."""
    # TODO: For all documents with ID=doc_id or any associated document:
    # TODO:   Remove entries from metadata with document=doc_id.
    # TODO:   Remove entry from documents where ID=doc_id
    # TODO:   Remove file from filesystem.


def create_attachment(parent, title="", author="", tags=[]):
    """Create a new attachment. Returns new ID."""
    timestamp = int(datetime.datetime.now().strftime("%s"))
    # TODO: INSERT INTO documents with type="attach" and parent=3
    # TODO: INSERT INTO metadata
    # TODO: register new tags
    return 41


def upload_doc(filepath, doc_id):
    """Take document from filepath and store it according to `doc_id`
    so we can retrieve it later. Also register at search engine and
    retrieve further metadata from the document. Returns None.
    """
    # retrieve file extension & mime type
    print(doc_id, filepath.filename)
    if '.' in filepath:
        fileext = filepath.filename.rsplit('.', 1)[1]
    else:
        fileext = str(doc_id)

    try:
        mimetype = mimetypes.types_map['.' + fileext]
    except KeyError:
        mimetype = None

    # move uploaded to repository
    file_path = os.path.join(UPLOAD_FOLDER, str(doc_id) + fileext)
    filepath.save(file_path)
    print('File {} stored.'.format(file_path))

    # TODO: store metadata entry: document=doc_id key='filename' value=file_path
    # TODO: store metadata entry: document=doc_id key='mimetype' value=mimetype
    # TODO: retrieve metadata using pdfminer, if PDF
    # TODO: add content to search engine, if plain text
    # TODO: add metadata to search engine
