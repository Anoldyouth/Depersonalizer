import pymorphy2
from sqlalchemy.orm import Session

from models.component import Component
from tests.factories.AbstractFactory import AbstractFactory


class ComponentFactory(AbstractFactory):
    def __init__(self, session: Session):
        super().__init__(session, Component)

    def definition(self) -> dict:
        name_functions = {
            'name': self.faker.first_name,
            'surname': self.faker.last_name,
            'last_name': self.faker.middle_name
        }

        comp_type = self.faker.random.choice(list(name_functions.keys()))
        comp = name_functions[comp_type]()
        morph = pymorphy2.MorphAnalyzer()
        parsed = morph.parse(comp)[0]

        if parsed.tag.gender in ('masc', 'femn'):
            gender = parsed.tag.gender
        else:
            gender = self.faker.random.choice(['masc', 'femn'])

        return {
            'type': comp_type,
            'component_nomn': parsed.inflect({'sing', 'nomn'}).word.title(),
            'component_gent': parsed.inflect({'sing', 'gent'}).word.title(),
            'component_datv': parsed.inflect({'sing', 'datv'}).word.title(),
            'component_accs': parsed.inflect({'sing', 'accs'}).word.title(),
            'component_ablt': parsed.inflect({'sing', 'ablt'}).word.title(),
            'component_loct': parsed.inflect({'sing', 'loct'}).word.title(),
            'gender': gender,
            'popularity': self.faker.random_int(min=1)
        }
