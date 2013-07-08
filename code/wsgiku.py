
from flask import Flask, request, jsonify, abort, Response, render_template
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.ext.declarative import declarative_base
import imp, sys, os, sqlalchemy, hashlib, time, random

def generate_app():
    app = Flask(__name__)
    app.config['PROPAGATE_EXCEPTIONS'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgres:///ealgis'
    from localsettings import SECRET_KEY
    app.config['SECRET_KEY'] = SECRET_KEY
    app.config['TESTING'] = True
    return app

app = generate_app()
db = SQLAlchemy(self.app)

class Haiku(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, null=False)
    parliament = db.Column(db.Integer, null=False)
    session = db.Column(db.Integer, null=False)
    period = db.Column(db.Integer, null=False)
    chamber = db.Column(db.String, null=False)
    text = db.Column(db.Text, null=False)