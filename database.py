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

    def __init__(self):
        print 'Document:' % (self.id)
        
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

    def __init__(self):
        print 'Metadata:' % (self.id)
        
    def __repr__(self):
        return self.key