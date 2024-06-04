import requests


class SarClient:
    def __init__(self, host: str, master_token: str):
        self.host = host
        self.master_token = master_token

    def search_address_items(self, search_string: str, address_type: int):
        params = {'search_string': search_string, 'address_type': address_type}
        headers = {'master-token': self.master_token, 'accept': 'application/json'}

        response = requests.get(f'{self.host}/SearchAddressItems', params=params, headers=headers)
        if response.status_code == 200:
            return response.json()

        raise Exception(f'search_address_items: {{status: {response.status_code}, message: {response.text}}}')

    def get_address_item_by_id(self, object_id: int, address_type: int):
        params = {'object_id': object_id, 'address_type': address_type}
        headers = {'master-token': self.master_token, 'accept': 'application/json'}

        response = requests.get(f'{self.host}/GetAddressItemById', params=params, headers=headers)
        if response.status_code == 200:
            return response.json()

        raise Exception(f'get_address_item_by_id: {{status: {response.status_code}, message: {response.text}}}')
