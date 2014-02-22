from nose import with_setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqla_helpers.tests.class_test import Treatment, Status


from sqla_helpers.base_model import BaseModel
from sqla_helpers.logical import Q
from sqla_helpers.tests.class_test import metadata

engine = create_engine('sqlite://')
session = sessionmaker(bind=engine)()

def populate():
    BaseModel.register_sessionmaker(session, force=True)
    metadata.create_all(engine)
    status = [Status(u'ok'), Status(u'ko')]
    session.add_all(status)

    ok  = status[0]
    for i in xrange(10):
        tr = Treatment(u'test {}'.format(i), ok)
        session.add(tr)

    ko = status[1]
    for i in xrange(8):
        tr = Treatment(u'test_ko {}'.format(i), ko)
        session.add(tr)

    session.commit()
	

def unpopulate():
	session.query(Treatment).delete()
	session.query(Status).delete()
	session.commit()



@with_setup(populate, unpopulate)
def test_dump():
    tr = Treatment.get(id=1)
    assert tr.dump() == {
      'id': 1,
      'status_id': 1,
      'status': {
        'id': 1,
        'name': u'ok'
      },
      'name': u'test 0',
    } 
    assert tr.dump(excludes=['status']) == {
      'id': 1,
      'status_id': 1,
      'name': u'test 0',
    }
    assert tr.dump(depth=1) == {
      'id': 1,
      'status_id': 1,
      'name': u'test 0',
    }


@with_setup(populate, unpopulate)
def test_load():
	status = Status.load({'name': u'plop'})
	assert status.name == u'plop'
	status = Status.load({'id': 1})
	assert status.id == 1 
	assert status.name == u'ok'


@with_setup(populate, unpopulate)
def test_coeherence():
    tr = Treatment.get(id=1)
    tr2 = Treatment.load(tr.dump())
    assert tr == tr2
