import array
import calendar
import datetime
import random
import re

from dateutil.relativedelta import relativedelta

from config.config import YEAR_DELTA
from entity_type import EntityType
from transformations.abstract_transformation import AbstractTransformation


class DateTransformation(AbstractTransformation):
    _year_delta: int = YEAR_DELTA
    _date_patterns: array = [
        r'(\d{1,2})[ ./-](\d{1,2})[ ./-](\d{4})',
        r'(\d{1,2})[ ./-]([а-яё]+)[ ./-](\d{4})',
        r'(\d{1,2}) ([а-яё]+) (\d{4})',
        r'(\d{1,2})-го ([а-яё]+) (\d{4})'
    ]

    def __init__(self):
        self._transformed_date = None

    def transform(self, date_input: str) -> str:
        match: re.Match | None = None
        for pattern in self._date_patterns:
            match = re.match(pattern, date_input)
            if match:
                break

        # Возможно, не поддерживаемый тип даты, замена на заглушку
        if not match:
            return f"<{EntityType.DATE.value}>"

        day = match.group(1)
        day_start, day_end = match.span(1)

        month = match.group(2)
        month_start, month_end = match.span(2)

        year = match.group(3)
        year_start, year_end = match.span(3)

        months = {
            'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4, 'мая': 5, 'июня': 6,
            'июля': 7, 'августа': 8, 'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
        }
        from_array = False
        if month in months:
            from_array = True
            month = months[month]

        date = datetime.datetime(int(year), int(month), int(day))
        date_now = datetime.datetime.now()
        fourteen = date_now - relativedelta(years=14)
        eighteen = date_now - relativedelta(years=18)

        if date <= eighteen:
            min_border = date - relativedelta(years=self._year_delta)
            max_border = min(date + relativedelta(years=self._year_delta), eighteen)
        elif date <= fourteen:
            min_border = max(date - relativedelta(years=self._year_delta), eighteen)
            max_border = min(date + relativedelta(years=self._year_delta), fourteen)
        else:
            min_border = max(date - relativedelta(years=self._year_delta), fourteen)
            max_border = date + relativedelta(years=self._year_delta)

        random_date = min_border + (max_border - min_border) * random.random()
        self._transformed_date = random_date

        return (date_input[:day_start] + str(random_date.day).zfill(len(day)) + date_input[day_end:month_start]
                + (calendar.month_name[random_date.month] if from_array else str(random_date.month).zfill(len(month)))
                + date_input[month_end:year_start] + str(random_date.year) + date_input[year_end:])

    def get_transformed_date(self) -> datetime.date | None:
        return self._transformed_date
