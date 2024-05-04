import random
import re
import string

from transformations.abstract_transformation import AbstractTransformation


class EmailTransformation(AbstractTransformation):
    _email_regex: str = r'^([a-zA-Z0-9._%+-]+)@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    def transform(self, email_input: str) -> str:
        match = re.match(self._email_regex, email_input)

        # Значит строка - не электронная почта, не преобразуем
        if not match:
            return email_input

        name_start, name_end = match.span(1)

        characters = string.ascii_letters + string.digits
        new_name = "".join(random.choice(characters) for _ in range(name_end))

        return new_name + email_input[name_end:]
