import os
import random
import re
from xml.etree import ElementTree

from clients.sar_client import SarClient
from config.config import SAR_HOST, SAR_MASTER_KEY, MAX_LEVEL
from entity_type import EntityType
from transformations.abstract_transformation import AbstractTransformation


class AddressTransformation(AbstractTransformation):
    sar_client = SarClient(SAR_HOST, SAR_MASTER_KEY)
    max_level = MAX_LEVEL

    def transform(self, address_input: str) -> str:
        address_type: int = 1
        try:
            for i in [1, 2]:
                addresses = self.sar_client.search_address_items(address_input, i)['addresses']

                if addresses:
                    address_type = i
                    break

            # Возвращаем заглушку, так как не знаем, что делать с адресом, а это персональные данные
            if not addresses:
                return f'<{EntityType.LOCATION.value}>'
        except Exception:
            # Не смогли получить данные от сервиса из-за ошибки, нет возможности обезличить
            return f'<{EntityType.LOCATION.value}>'

        address = addresses[0]  # Найденный адрес
        path: str = str(address['hierarchy'][0]['object_id'])
        region_code: str = str(address['hierarchy'][0]['region_code'])
        replacing_indexes = []

        # Составляем маску искомого пути адреса
        for index, component in enumerate(address['hierarchy'][1:]):
            if 'object_level_id' in component and int(component['object_level_id']) <= self.max_level:
                path += f'.{component["object_id"]}'
            else:
                replacing_indexes.append(index + 1)
                path += f'.\\d'

        try:
            replace_address_id = self.__search_in_xml(address_type, region_code, path, str(address['object_id']))
        except Exception:
            # Не смогли получить данные от сервиса из-за ошибки, нет возможности обезличить
            return f'<{EntityType.LOCATION.value}>'

        # Возвращаем заглушку, так как по каким-то неизвестным причинам мы не смогли найти аналога данного адреса
        # В реальных условиях кейс невозможен
        if not addresses:
            return f'<{EntityType.LOCATION.value}>'

        replace_address = self.sar_client.get_address_item_by_id(replace_address_id, address_type)['addresses'][0]
        address_output = self.__make_replace(address, replace_address, replacing_indexes, address_input)

        return address_output

    @staticmethod
    def __search_in_xml(address_type: int, region_code: str, path_prepared: str, exclude_id: str) -> int | None:
        current_directory = os.path.dirname(os.path.abspath(__file__))
        directory = f'{current_directory}/../../sar/{region_code.zfill(2)}'
        filename_start = 'AS_ADM_HIERARCHY' if address_type == 1 else 'AS_MUN_HIERARCHY'

        files_in_directory = os.listdir(directory)
        matching_file: str | None = None
        for file in files_in_directory:
            if file.startswith(filename_start):
                matching_file = file
                break

        if not matching_file:
            return None

        tree = ElementTree.parse(f'{directory}/{matching_file}')
        root = tree.getroot()

        matching_items = []

        path_regex = re.compile(path_prepared)
        for item in root.findall('.//ITEM'):
            path = item.get('PATH')
            is_active = item.get('ISACTIVE') == "1"
            if path_regex.match(path) and is_active:
                matching_items.append(item.get('OBJECTID'))

        if not matching_items:
            return None

        random.shuffle(matching_items)
        for item in matching_items:
            if item != exclude_id:
                return int(item)

        return None

    @staticmethod
    def __make_replace(
            address: dict,
            replace_address: dict,
            replacing_indexes: list,
            address_input: str
    ) -> str:
        address_output = address_input
        for replace_index in replacing_indexes:
            # Замена названия объекта
            name_pattern = re.compile(
                r'\b' + re.escape(address['hierarchy'][replace_index]['name']) + r'\b',
                re.IGNORECASE
            )
            address_output = name_pattern.sub(replace_address['hierarchy'][replace_index]['name'], address_output)

            # Замена типа объекта
            type_name_pattern = re.compile(
                r'\b' + re.escape(address['hierarchy'][replace_index]['type_name']) + r'\b',
                re.IGNORECASE
            )
            address_output = type_name_pattern.sub(
                replace_address['hierarchy'][replace_index]['type_name'],
                address_output
            )

            # Замена сокращенного типа объекта
            type_short_name_pattern = re.compile(
                r'\b' + re.escape(address['hierarchy'][replace_index]['type_short_name']) + r'\b',
                re.IGNORECASE
            )
            address_output = type_short_name_pattern.sub(
                replace_address['hierarchy'][replace_index]['type_short_name'],
                address_output
            )

        return address_output
