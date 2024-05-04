from abc import ABC

from faker import Faker
from sqlalchemy.orm import Session


class AbstractFactory(ABC):
    faker = Faker('ru_RU')

    def __init__(self, session: Session, class_variable):
        self.session = session
        self.class_variable = class_variable

    def definition(self) -> dict:
        return NotImplemented

    def make(self, extra=None):
        if extra is None:
            extra = {}
        params = self.definition()
        params.update(extra)

        return self.class_variable(**params)

    def create(self, extra=None):
        obj = self.make(extra)
        self.session.add(obj)
        self.session.commit()
        self.session.refresh(obj)

        return obj
