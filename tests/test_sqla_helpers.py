from mock import Mock

from sqla_helpers.base_model import BaseModel

Session = Mock()

BaseModel.register_sessionmaker(lambda: Session)

class MyInstrumentedAttribut(Mock):
    """
    Simule un instrumentedAttribut d'SQLAlchemy
    """
    def __init__(self, cls_=None, *args, **kwargs):
        super(MyInstrumentedAttribut, self).__init__(*args, **kwargs)
        self.property.mapper.class_ = cls_


class Titi(Mock, BaseModel):
    pass

class Toto(Mock, BaseModel):
    id = MyInstrumentedAttribut()
    attr = MyInstrumentedAttribut(Titi)


def test_session():
    assert BaseModel.session == Session
    BaseModel.register_sessionmaker(Mock(return_value=Session))
    assert BaseModel.session == Session

def test_all():
    Toto.all()
    Toto.session.query.assert_called_with(Toto)

def test_get():
    Toto.get()
    Toto.session.query.assert_called_with(Toto)

def test_filter():
    Toto.filter(id=3)
    Toto.session.query.assert_called_with(Toto)
