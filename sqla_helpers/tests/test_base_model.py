from mock import Mock

from sqla_helpers.base_model import BaseModel




def test_session():
    Session = Mock()
    BaseModel.register_sessionmaker(lambda: Session)
    assert BaseModel.session == Session
