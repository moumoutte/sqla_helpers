from nose import with_setup
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from sqla_helpers.tests.class_test import Treatment, Status


from sqla_helpers.base_model import BaseModel
from sqla_helpers.tests.class_test import metadata

engine = create_engine('sqlite://')
session = sessionmaker(bind=engine)()

def populate():
	BaseModel.register_sessionmaker(lambda: session)
	metadata.create_all(engine)
	status = [Status(u'ok'), Status(u'ko')]
	session.add_all(status)
	session.commit()
	

def unpopulate():
	session.query(Treatment).delete()
	session.query(Status).delete()
	session.commit()


@with_setup(populate, unpopulate)
def test_load():
	status = Status.load({'name': u'plop'})
	assert status.name == u'plop'
	status = Status.load({'id': 1})
	assert status.id == 1 
	assert status.name == u'ok'
