import json
import os
import shutil
from unittest.mock import Mock, patch

import pytest
from alembic.command import upgrade
from freezegun import freeze_time

from config.connection import DatabaseHelper
from depersonalizer import Depersonalizer
from entity_type import EntityType
from models.component import Component
from utils import alembic_config_from_url

test_string = (
    'Я, Иванов Иван Иванович, проживающий по адресу Россия, Москва, Зеленоград, Крюковская пл., д. 1,'
    ' родился 10.03.2001, подтверждаю паспортом с серией 1234 номером 567890.'
    ' Связаться можно по номеру телефона +7(800)555-35-35 или почте test@mail.com'
)

test_region = 0
content = """<?xml version="1.0" encoding="utf-8"?>
<ITEMS>
    <ITEM ID="1" OBJECTID="1" ISACTIVE="1" PATH="77.10.1006.1050" />
    <ITEM ID="2" OBJECTID="2" ISACTIVE="1" PATH="77.10.6004.1006" />
</ITEMS>"""

search_address_items_response = """{
  "addresses": [
    {
      "object_id": 1,
      "object_level_id": 8,
      "path": "77.10.1006.1050",
      "hierarchy": [
        {
          "object_id": 2,
          "object_level_id": 1,
          "region_code": 0,
          "name": "Москва",
          "type_name": "Город",
          "type_short_name": "г"
        },
        {
          "object_id": 3,
          "object_level_id": 5,
          "name": "Зеленоград",
          "type_name": "Город",
          "type_short_name": "г"
        },
        {
          "object_id": 4,
          "object_level_id": 7,
          "name": "Крюковская",
          "type_name": "Площадь",
          "type_short_name": "пл"
        },
        {
          "object_id": 5,
          "object_level_id": 8,
          "name": "1",
          "type_name": "Дом",
          "type_short_name": "д"
        }
      ]
    }
  ]
}"""

get_address_item_by_id_response = """{
  "addresses": [
    {
      "object_id": 2,
      "object_level_id": 10,
      "path": "77.10.6004.1006",
      "hierarchy": [
        {
          "object_id": 2,
          "object_level_id": 1,
          "region_code": 0,
          "name": "Москва",
          "type_name": "Город",
          "type_short_name": "г"
        },
        {
          "object_id": 3,
          "object_level_id": 5,
          "name": "Зеленоград",
          "type_name": "Город",
          "type_short_name": "г"
        },
        {
          "object_id": 4,
          "object_level_id": 7,
          "name": "Панфиловский",
          "type_name": "Проспект",
          "type_short_name": "пр-кт"
        },
        {
          "object_id": 5,
          "object_level_id": 8,
          "name": "21",
          "type_name": "Дом",
          "type_short_name": "д"
        }
      ]
    }
  ]
}"""

component_from_name = Component(
    id=1,
    type='name',
    component_nomn='Иван',
    component_gent='Ивана',
    component_datv='Ивану',
    component_accs='Ивана',
    component_ablt='Иваном',
    component_loct='Иване',
    gender='masc',
    popularity=100
)
component_from_surname = Component(
    id=2,
    type='surname',
    component_nomn='Иванов',
    component_gent='Иванова',
    component_datv='Иванову',
    component_accs='Иванова',
    component_ablt='Ивановым',
    component_loct='Иванове',
    gender='masc',
    popularity=100
)
component_from_last_name = Component(
    id=3,
    type='last_name',
    component_nomn='Иванович',
    component_gent='Ивановича',
    component_datv='Ивановичу',
    component_accs='Ивановича',
    component_ablt='Ивановичем',
    component_loct='Ивановиче',
    gender='masc',
    popularity=100
)

component_to_name = Component(
    id=4,
    type='name',
    component_nomn='Сергей',
    component_gent='Сергея',
    component_datv='Сергею',
    component_accs='Сергея',
    component_ablt='Сергеем',
    component_loct='Сергее',
    gender='masc',
    popularity=100
)
component_to_surname = Component(
    id=5,
    type='surname',
    component_nomn='Сергеев',
    component_gent='Сергеева',
    component_datv='Сергееву',
    component_accs='Сергеева',
    component_ablt='Сергеевым',
    component_loct='Сергееве',
    gender='masc',
    popularity=100
)
component_to_last_name = Component(
    id=6,
    type='last_name',
    component_nomn='Сергеевич',
    component_gent='Сергеевича',
    component_datv='Сергеевичу',
    component_accs='Сергеевича',
    component_ablt='Сергеевичем',
    component_loct='Сергеевиче',
    gender='masc',
    popularity=100
)

generated_string = (
    'Я, Сергеев Сергей Сергеевич, проживающий по адресу Россия,'
    ' Москва, Зеленоград, Панфиловский пр-кт., д. 21, родился 14.10.2000,'
    ' подтверждаю паспортом с серией 1220 номером 567123.'
    ' Связаться можно по номеру телефона +7(800)123-45-67 или почте dprs@mail.com'
)


@pytest.fixture
def make_migrations():
    alembic_config = alembic_config_from_url(DatabaseHelper().get_url())
    upgrade(alembic_config, 'head')


@pytest.fixture
def spacy_mock(mocker):
    spacy_nlp_mock = Mock()
    spacy_nlp_mock.return_value = Mock()
    spacy_nlp_mock.return_value.ents = [
        Mock(text="Иванов Иван Иванович", label_=EntityType.PERSON.value, start_char=3, end_char=23),
        Mock(
            text="Россия, Москва, Зеленоград, Крюковская пл., д. 1",
            label_=EntityType.LOCATION.value,
            start_char=47,
            end_char=95
        ),
        Mock(text="10.03.2001", label_=EntityType.DATE.value, start_char=105, end_char=115),
        Mock(text="с серией 1234 номером 567890", label_=EntityType.PASSPORT.value, start_char=139, end_char=167),
        Mock(text="+7(800)555-35-35", label_=EntityType.PHONE.value, start_char=204, end_char=220),
        Mock(text="test@mail.com", label_=EntityType.EMAIL.value, start_char=231, end_char=244),
    ]

    mocker.patch("depersonalizer.spacy.load", return_value=spacy_nlp_mock)

    return spacy_nlp_mock


@pytest.fixture
def request_mock(mocker):
    def get_response(url: str, *args, **kwargs):
        if url.endswith('/SearchAddressItems'):
            mock_search_items_response = Mock()
            mock_search_items_response.status_code = 200
            mock_search_items_response.json.return_value = json.loads(search_address_items_response)

            return mock_search_items_response
        elif url.endswith('/GetAddressItemById'):
            mock_get_address_item_by_id_response = Mock()
            mock_get_address_item_by_id_response.status_code = 200
            mock_get_address_item_by_id_response.json.return_value = json.loads(get_address_item_by_id_response)

            return mock_get_address_item_by_id_response

    mocker.patch("requests.get", side_effect=get_response)


@pytest.fixture
def adm_file():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    temp_dir = f'{current_directory}/../sar/{str(test_region).zfill(2)}'
    os.mkdir(temp_dir)

    temp_adm = os.path.join(temp_dir, "AS_ADM_HIERARCHY_test.xml")
    with open(temp_adm, "w") as f_adm:
        f_adm.write(content)

    yield temp_adm

    shutil.rmtree(temp_dir)


@pytest.fixture
def prepare_db():
    session = DatabaseHelper().get_session()
    session.add_all(
        [component_from_name, component_from_surname, component_from_last_name,
         component_to_name, component_to_surname, component_to_last_name]
    )
    session.commit()

    yield session

    session.delete(component_from_name)
    session.delete(component_from_surname)
    session.delete(component_from_last_name)
    session.delete(component_to_name)
    session.delete(component_to_surname)
    session.delete(component_to_last_name)
    session.commit()
    session.close()


@pytest.fixture
def mocked_random():
    with (
        patch('random.randint') as mock_randint,
        patch('random.choice') as mock_choice,
        patch('random.random') as mock_random
    ):
        mock_random.side_effect = [0.4]
        mock_randint.side_effect = [
            123, 45, 67,
            567123
        ]
        mock_choice.side_effect = [
            'd', 'p', 'r', 's'
        ]

        yield mock_randint, mock_choice, mock_random


@freeze_time("2024-06-01")
def test_depersonalize_success(make_migrations, spacy_mock, request_mock, adm_file, prepare_db, mocked_random):
    # Вызываем функцию, которую мы тестируем
    new_string = Depersonalizer().handle(test_string)

    assert new_string == generated_string
