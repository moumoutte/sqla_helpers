from mock import Mock

from sqla_helpers.base_model import BaseModel

Session = Mock()

BaseModel.register_sessionmaker(lambda: Session)



def test_session():
    assert BaseModel.session == Session
    BaseModel.register_sessionmaker(Mock(return_value=Session))
    assert BaseModel.session == Session

