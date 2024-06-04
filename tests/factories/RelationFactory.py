from sqlalchemy.orm import Session

from models.component import Relation
from tests.factories.AbstractFactory import AbstractFactory
from tests.factories.ComponentFactory import ComponentFactory


class RelationFactory(AbstractFactory):
    def __init__(self, session: Session):
        super().__init__(session, Relation)

    def definition(self) -> dict:
        first = ComponentFactory().create().id
        second = ComponentFactory().create().id

        return {
            'component_id_1': first,
            'component_id_2': second
        }
