from enum import Enum


class EntityType(Enum):
    PERSON = 'PER'
    LOCATION = 'LOC'
    DATE = 'DATE'
    PHONE = 'PHONE'
    EMAIL = 'EMAIL'
    PASSPORT = 'PASSPORT'

    def sort_key(self, record):
        # Сначала записи с меткой 'DATE', затем все остальные
        return record['ent']['label_'] != 'DATE', record['text']
