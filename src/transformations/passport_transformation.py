import datetime
import random
import re

from dateutil.relativedelta import relativedelta

from config.config import YEAR_DELTA
from transformations.abstract_transformation import AbstractTransformation


class PassportTransformation(AbstractTransformation):
    _passport_regex: str = r'\d{2}(\d{2})\D*(\d{6})'
    _year_delta: int = YEAR_DELTA

    def __init__(self, transformed_date: datetime.date | None):
        self._transformed_date = transformed_date

    def transform(self, passport_input: str) -> str:
        now = datetime.datetime.now()
        match = re.search(self._passport_regex, passport_input)

        # Значит строка - не паспортные данные, не заменяем
        if not match:
            return passport_input

        series_year = match.group(1)
        series_year_start, series_year_end = match.span(1)
        number_start, number_end = match.span(2)

        if self._transformed_date:
            fourteen = self._transformed_date + relativedelta(years=14)
            twenty = self._transformed_date + relativedelta(years=20)
            forty_five = self._transformed_date + relativedelta(years=45)

            if now <= twenty:
                new_series_year = fourteen.year
            elif now <= forty_five:
                new_series_year = twenty.year
            else:
                new_series_year = forty_five.year
        else:
            new_series_year = random.randint(
                int(series_year) - int(self._year_delta),
                int(series_year) + int(self._year_delta)
            )

        new_number = random.randint(100_000, 999_999)

        return (passport_input[:series_year_start] + str(new_series_year).zfill(4)[2:]
                + passport_input[series_year_end:number_start] + str(new_number) + passport_input[number_end:])
