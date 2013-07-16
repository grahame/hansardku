
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
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), nullable=False)
    poem_uid = db.Column(db.String, nullable=False, index=True)
    talker_id = db.Column(db.String, nullable=False)
    talker = db.Column(db.String, nullable=False)
    party = db.Column(db.String)
    poem = db.Column(db.Text, nullable=False)
    # trails    
    poem_index = db.Column(db.Integer, primary_key=True)
    talker_index = db.Column(db.Integer, nullable=False)
    __table_args__ = (
        sqlalchemy.Index('talker_trail_idx', talker_id, talker_index), )

class HaikuTrail(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String, nullable=False)
    length = db.Column(db.Integer, nullable=False)

class PoemFinder:
    # pattern credit: http://stackoverflow.com/questions/42558/python-and-the-singleton-pattern
    _instance = None
    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PoemFinder, cls).__new__(cls, *args, **kwargs)
            cls._instance._made = False
        return cls._instance

    def __init__(self):
        # load in the trails
        self.trails = {}
        for trail in db.session.query(HaikuTrail).all():
            self.trails[trail.key] = trail

    def poem_for_trail(self, trail, at_row=None):
        npossible = self.trails[trail].length
        if at_row is not None and at_row < npossible:
            npossible -= 1
        idx = int(random.random() * npossible)
        if at_row is not None:
            if idx >= at_row:
                idx += 1
        if trail.startswith('talker='):
            tid = trail.split('=', 1)[1]
            poem = db.session.query(Haiku).filter(Haiku.talker_id==tid, Haiku.talker_index==idx).one()
        elif trail == 'all':
            poem = db.session.query(Haiku).filter(Haiku.poem_index==idx).one()
        else:
            return
        return self.poem_response(poem)

    def poem_by_uid(self, uid):
        poem = db.session.query(Haiku).filter(Haiku.poem_uid==uid).one()
        return self.poem_response(poem)

    def poem_response(self, poem):
        return {
            'text': poem.poem.splitlines(),
            'hash': poem.poem_uid,
            'talker_id': poem.talker_id,
            'talker': poem.talker,
            'party' : poem.party,
            'date': poem.document.date.strftime("%a, %d %B %Y"),
            'talker_index': poem.talker_index,
            'poem_index': poem.poem_index
        }

@app.route("/api/0.1/haiku/issue/<path>")
def get_haiku(path):
    finder = PoemFinder()
    data = finder.poem_for_trail(path)
    if data is None:
        abort(404)
    return jsonify(data)

@app.route("/api/0.1/haiku/issue/<path>/<from_index>")
def get_haiku_from(path, from_index):
    finder = PoemFinder()
    data = finder.poem_for_trail(path, int(from_index))
    if data is None:
        abort(404)
    return jsonify(data)

@app.route("/api/0.1/haiku/byuid/<uid>")
def get_haiku_uid(uid):
    finder = PoemFinder()
    return jsonify(finder.poem_by_uid(uid))
