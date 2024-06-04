import datetime
from abc import ABC


class AbstractTransformation(ABC):
    def transform(self, input_string):
        pass

    def get_transformed_date(self) -> datetime.date | None:
        return None
