from flask.ext.sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Document(db.Model):
    __tablename__ = "documents"
    id = db.Column(db.Integer, primary_key = True)
    type = db.Column(db.String(20))
    title = db.Column(db.String(256))
    author = db.Column(db.String(40))
    timestamp = db.Column(db.Integer)
    parent = db.Column(db.Integer)

    def __init__(self, type='doc', title='', author='', \
                 timestamp=None, parent=None):
        if not timestamp:
            timestamp = int(datetime.now().strftime("%s"))

        self.type = type
        self.title = title
        self.author = author
        self.timestamp = timestamp
        self.parent = parent
        
    def __repr__(self):
        return self.title

    def getDate(self):
        return datetime.utcfromtimestamp(self.timestamp)
    
    def getFormatDateString(self):
        return self.getDate().strftime('%Y-%m-%d')


class Metadata(db.Model):
    __tablename__ = "metadata"
    id = db.Column(db.Integer, primary_key = True)
    document = db.Column(db.Integer)
    key = db.Column(db.String(40))
    value = db.Column(db.Text)

    def __init__(self, document, key, value=''):
        self.document = document
        self.key = key
        self.value = value
        
    def __repr__(self):
        return self.key
