
from flask import Flask, request, jsonify, abort, Response, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
import imp, sys, os, sqlalchemy, hashlib, time, random

def generate_app():
    app = Flask(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///hansardku'
    from localsettings import SECRET_KEY
    app.config['SECRET_KEY'] = SECRET_KEY
    return app

app = generate_app()
db = SQLAlchemy(app)

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String, nullable=False)
    date = db.Column(db.Date, nullable=False)
    parliament = db.Column(db.Integer, nullable=False)
    session = db.Column(db.Integer, nullable=False)
    period = db.Column(db.Integer, nullable=False)
    chamber = db.Column(db.String, nullable=False)
    haiku = db.relationship('Haiku',
        backref=db.backref('document'),
        cascade="all",
        lazy='dynamic')

class Haiku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), index=True, nullable=False)
    poem_uid = db.Column(db.String, nullable=False, index=True)
    talker_id = db.Column(db.String, nullable=False, index=True)
    talker = db.Column(db.String, nullable=False, index=True)
    party = db.Column(db.String)
    poem = db.Column(db.Text, nullable=False)

class HaikuTrail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False)
    length = db.Column(db.Integer, nullable=False)
    entries = db.relationship('HaikuTrailEntry',
        backref=db.backref('haiku_trail'),
        cascade="all",
        lazy='dynamic')

class HaikuTrailEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    trail_id = db.Column(db.Integer, db.ForeignKey('haiku_trail.id'), nullable=False)
    trail_index = db.Column(db.Integer, nullable=False)
    from_haiku = db.Column(db.Integer, db.ForeignKey('haiku.id'), nullable=False)
    to_haiku = db.Column(db.Integer, db.ForeignKey('haiku.id'), nullable=False)
    __table_args__ = (db.Index('trail_from', "trail_id", "from_haiku"), db.Index('trail_to', "trail_id", "to_haiku"), db.UniqueConstraint('trail_id', 'trail_index'))
