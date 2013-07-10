#!/usr/bin/env python3

from lxml import etree
import sys, os, csv, hashlib, base62, time, string, numpy
from xml2text import xml2text
from haiku import token_stream, poem_finder, Syllables
from wsgiku import db, app, Document, Haiku

if __name__ == '__main__':
    db.create_all()
    db.session.commit()

    base_query = db.session.query(Haiku.id)

    def build_trail(name, query):
        trail_length = query.count()
        print("building trail `%s' -> %d" % (name, trail_length))
        ids = numpy.ndarray(trail_length)
        idx = 0
        for row in query.yield_per(8192):
            ids[idx] = row[0]
            idx += 1

    build_trail("/", base_query)
    for talker_id, in db.session.query(Haiku.talker_id).group_by(Haiku.talker_id).all():
        build_trail("/talker/" + talker_id, base_query.filter(Haiku.talker_id==talker_id))
