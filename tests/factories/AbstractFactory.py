from abc import ABC

from faker import Faker

from config.connection import DatabaseHelper


class AbstractFactory(ABC):
    database_helper = DatabaseHelper()
    faker = Faker('ru_RU')

    def __init__(self, class_variable):
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
        with self.database_helper.get_session() as session:
            obj = self.make(extra)
            session.add(obj)
            session.commit()
            session.refresh(obj)

        return obj
