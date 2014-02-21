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
def test_get():
  tr = Treatment.get(id=1)
  assert isinstance(tr, Treatment)


@with_setup(populate, unpopulate)
def test_filter():
  assert type(Treatment.filter(id=1)) == list
  assert len(Treatment.filter(id=1)) == 1
  assert len(Treatment.filter(~Q(id=1))) == 17
  assert len(Treatment.filter(status__name=u'ok')) == len(Treatment.filter(~Q(status__name=u'ko')))
