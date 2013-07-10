#!/usr/bin/env python3

from lxml import etree
import sys, os, csv, hashlib, base62, time, string, numpy, itertools, getpass
from xml2text import xml2text
from haiku import token_stream, poem_finder, Syllables
from wsgiku import db, app, Document, Haiku, HaikuTrail, HaikuTrailEntry

def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)

if __name__ == '__main__':

    def debug(s):
        sys.stderr.write(s)
        sys.stderr.flush()

    base_query = db.session.query(Haiku.id)
    next_trail_id = itertools.count()

    db.create_all()
    db.session.commit()

    # pull the indexes off the HaikuTrailEnty
    debug("removing indexes: ")
    [t.drop(bind=db.engine) for t in HaikuTrailEntry.__table__.indexes]
    db.session.commit()
    debug("done.\n")

    def build_trail(name, query):
        debug("%s: finding count... " % (name))
        trail_length = query.count()
        debug("%d\n" % trail_length)
        ids = numpy.ndarray(trail_length, dtype=int)
        ny = 100000
        debug("load haiku IDs: ")
        for idx, row in enumerate(query.yield_per(ny)):
            ids[idx] = row[0]
        assert(idx == trail_length - 1)
        numpy.random.shuffle(ids)
        debug("done.\n")
        trail = HaikuTrail(key=name, length=trail_length)
        db.session.add(trail)
        db.session.commit()
        trail_csv = os.path.join("/run/user/", getpass.getuser(), 'trail.csv')
        debug("writing trail to CSV: ")
        with open(trail_csv, 'w') as fd:
            w = csv.writer(fd)
            for trail_index, (from_id, to_id) in enumerate(pairwise(ids)):
                w.writerow((next(next_trail_id), trail.id, trail_index, from_id, to_id))
        debug("done.\n")
        debug("importing CSV: ")
        conn = db.session.connection()
        res = conn.execute('COPY %s FROM %%s CSV' % ('haiku_trail_entry'), (trail_csv, ))
        os.unlink(trail_csv)
        db.session.commit()
        debug("done.\n")

    debug("determining talkers... ")
    talker_query = db.session.query(Haiku.talker_id).group_by(Haiku.talker_id)
    talkers = [t[0] for t in talker_query.all()]
    talkers.sort()
    debug("done.\n")
    for idx, talker_id in enumerate(talkers):
        debug("(%d/%d) %s\n" % (idx+1, len(talkers), talker_id))
        build_trail("/talker/" + talker_id, base_query.filter(Haiku.talker_id==talker_id))
    build_trail("/", base_query)

    debug("adding the indexes back... ")
    db.create_all()
    db.session.commit()
    debug("done.\n")
