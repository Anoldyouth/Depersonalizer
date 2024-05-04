import json
import os
import shutil
from unittest.mock import patch, MagicMock, Mock

import pytest

from transformations.address_transformation import AddressTransformation

test_region = 0
content = """<?xml version="1.0" encoding="utf-8"?>
<ITEMS>
    <ITEM ID="1" OBJECTID="1" ISACTIVE="1" PATH="2.3.4.5.6" />
    <ITEM ID="2" OBJECTID="2" ISACTIVE="1" PATH="2.3.7.8.9" />
    <ITEM ID="3" OBJECTID="3" ISACTIVE="0" PATH="2.3.10.11.12" />
    <ITEM ID="4" OBJECTID="4" ISACTIVE="1" PATH="2.3.13.14.15" />
    <ITEM ID="5" OBJECTID="5" ISACTIVE="1" PATH="2.3.13.14.15.16" />
    <ITEM ID="6" OBJECTID="6" ISACTIVE="1" PATH="2.3.13.14" />
    <ITEM ID="7" OBJECTID="7" ISACTIVE="1" PATH="100.101.102.103.104" />
</ITEMS>"""

search_address_items_response = """{
  "addresses": [
    {
      "object_id": 1,
      "object_level_id": 10,
      "path": "2.3.4.5.6",
      "hierarchy": [
        {
          "object_id": 2,
          "object_level_id": 1,
          "region_code": 0,
          "name": "Первый",
          "type_name": "Объект_1",
          "type_short_name": "Об_1"
        },
        {
          "object_id": 3,
          "object_level_id": 5,
          "name": "Второй",
          "type_name": "Объект_2",
          "type_short_name": "Об_2"
        },
        {
          "object_id": 4,
          "object_level_id": 7,
          "name": "Третий",
          "type_name": "Объект_3",
          "type_short_name": "Об_3"
        },
        {
          "object_id": 5,
          "object_level_id": 8,
          "name": "Четвертый",
          "type_name": "Объект_4",
          "type_short_name": "Об_4"
        },
        {
          "object_id": 6,
          "object_level_id": 10,
          "name": "Пятый",
          "type_name": "Объект_5",
          "type_short_name": "Об_5"
        }
      ]
    }
  ]
}"""

get_address_item_by_id_response = """{
  "addresses": [
    {
      "object_id": 5,
      "object_level_id": 10,
      "path": "2.3.13.14.15",
      "hierarchy": [
        {
          "object_id": 2,
          "object_level_id": 1,
          "region_code": 0,
          "name": "First",
          "type_name": "Object_1",
          "type_short_name": "Obj_1"
        },
        {
          "object_id": 3,
          "object_level_id": 5,
          "name": "Second",
          "type_name": "Object_2",
          "type_short_name": "Obj_2"
        },
        {
          "object_id": 4,
          "object_level_id": 7,
          "name": "Third",
          "type_name": "Object_3",
          "type_short_name": "Obj_3"
        },
        {
          "object_id": 5,
          "object_level_id": 8,
          "name": "Fourth",
          "type_name": "Object_4",
          "type_short_name": "Obj_4"
        },
        {
          "object_id": 6,
          "object_level_id": 10,
          "name": "Fifth",
          "type_name": "Object_5",
          "type_short_name": "Obj_5"
        }
      ]
    }
  ]
}"""


@pytest.fixture
def prepare_env():
    os.environ['SAR_HOST'] = '127.0.0.1'
    os.environ['SAR_MASTER_KEY'] = 'key'
    os.environ['MAX_LEVEL'] = '6'


@pytest.fixture
def adm_file():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    temp_dir = f'{current_directory}/../../sar/{str(test_region).zfill(2)}'
    os.mkdir(temp_dir)

    temp_adm = os.path.join(temp_dir, "AS_ADM_HIERARCHY_test.xml")
    with open(temp_adm, "w") as f_adm:
        f_adm.write(content)

    yield temp_adm

    shutil.rmtree(temp_dir)


@patch('random.shuffle')
def test_address_transformation_adm(mock_shuffle: MagicMock, adm_file, prepare_env):
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

    transformation = AddressTransformation()

    with patch('requests.get', side_effect=get_response) as request_get_mock:
        mock_shuffle.side_effect = lambda x: x

        new_address = transformation.transform(
            "Первый объект_1, Второй об_2, третий Объект_3, четвертый Об_4, пятый объект_5"
        )

        assert new_address == 'Первый объект_1, Второй об_2, Third Object_3, Fourth Obj_4, Fifth Object_5'

        assert request_get_mock.call_count == 2
        assert request_get_mock.mock_calls[1].kwargs['params']['object_id'] == 2
        assert request_get_mock.mock_calls[1].kwargs['params']['address_type'] == 1


@pytest.fixture
def mun_file():
    current_directory = os.path.dirname(os.path.abspath(__file__))

    temp_dir = f'{current_directory}/../../sar/{str(test_region).zfill(2)}'
    os.mkdir(temp_dir)

    temp_mun = os.path.join(temp_dir, "AS_MUN_HIERARCHY_test.xml")
    with open(temp_mun, "w") as f_mun:
        f_mun.write(content)

    yield temp_mun

    shutil.rmtree(temp_dir)


@patch('random.shuffle')
def test_address_transformation_mun(mock_shuffle: MagicMock, mun_file, prepare_env):
    def get_response(url: str, *args, **kwargs):
        if kwargs['params']['address_type'] == 1:
            response = Mock()
            response.status_code = 200
            response.json.return_value = json.loads('{"addresses": []}')

            return response

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

    transformation = AddressTransformation()

    with patch('requests.get', side_effect=get_response) as request_get_mock:
        mock_shuffle.side_effect = lambda x: x

        new_address = transformation.transform(
            "Первый объект_1, Второй об_2, третий Объект_3, четвертый Об_4, пятый объект_5"
        )

        assert new_address == 'Первый объект_1, Второй об_2, Third Object_3, Fourth Obj_4, Fifth Object_5'

        assert request_get_mock.call_count == 3
        assert request_get_mock.mock_calls[2].kwargs['params']['object_id'] == 2
        assert request_get_mock.mock_calls[2].kwargs['params']['address_type'] == 2


def test_address_not_found(prepare_env):
    def get_response(url: str, *args, **kwargs):
        response = Mock()
        response.status_code = 200
        response.json.return_value = json.loads('{"addresses": []}')

        return response

    transformation = AddressTransformation()

    with patch('requests.get', side_effect=get_response) as request_get_mock:

        new_address = transformation.transform(
            "Первый объект_1, Второй об_2, третий Объект_3, четвертый Об_4, пятый объект_5"
        )

        assert new_address == '<LOC>'
