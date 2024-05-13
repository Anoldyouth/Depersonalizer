import random
import re

from src.entity_type import EntityType
from src.transformations.abstract_transformation import AbstractTransformation


class PhoneTransformation(AbstractTransformation):
    _phone_regex: str = r'(?:(?:\+7|8)(?:\s|\()?)?(\d{3})(?:\s|\))?(\d{3})(?:\-|\s)?(\d{2})(?:\-|\s)?(\d{2})'

    def transform(self, phone_input: str) -> str:
        match = re.search(self._phone_regex, phone_input)

        # Значит строка - не номер телефона, не преобразуем
        if not match:
            return f"<{EntityType.PHONE.value}>"

        first_start, first_end = match.span(2)
        second_start, second_end = match.span(3)
        third_start, third_end = match.span(4)

        return (phone_input[:first_start] + str(random.randint(0, 999)).zfill(3)
                + phone_input[first_end:second_start] + str(random.randint(0, 99)).zfill(2)
                + phone_input[second_end:third_start] + str(random.randint(0, 99)).zfill(2)
                + phone_input[third_end:])