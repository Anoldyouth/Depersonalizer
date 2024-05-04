import locale
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from transformations.date_transformation import DateTransformation


@pytest.fixture
def prepared_transformation():
    transformation = DateTransformation()
    transformation._year_delta = 2

    yield transformation


@freeze_time("2024-06-01")
@pytest.mark.parametrize('date,fixed_random,expected', [
    ('01.01.2020', 1, '01.01.2022'),  # Меньше 14 лет
    ('01.01.2011', 0, '01.06.2010'),  # 13 лет, минимальная граница
    ('01.01.2009', 1, '01.06.2010'),  # 15 лет, максимальная граница
    ('01.01.2007', 0, '01.06.2006'),  # 17 лет, минимальная граница
    ('01.01.2005', 1, '01.06.2006'),  # 19 лет, минимальная граница
    ('01.01.2005', 0, '01.01.2003'),  # 19 лет, минимальная граница
])
def test_date_transformation_different_intervals(prepared_transformation, date: str, fixed_random: int, expected: str):
    with patch('random.random') as mock_random:
        mock_random.return_value = fixed_random

        new_date = prepared_transformation.transform(date)

    assert new_date == expected
    assert prepared_transformation.get_transformed_date() is not None


@freeze_time("2024-06-01")
@pytest.mark.parametrize('date,expected', [
    ('01-01-2000', '08-08-1999'),
    ('1-1-2000', '8-8-1999'),
    ('01.01.2000', '08.08.1999'),
    ('1.1.2000', '8.8.1999'),
    ('01 января 2000', '08 августа 1999'),
    ('1 января 2000', '8 августа 1999'),
    ('01-го января 2000', '08-го августа 1999'),
    ('1-го января 2000', '8-го августа 1999'),
])
def test_date_transformation_different_formats(date: str, expected: str):
    locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')
    transformation = DateTransformation()

    with patch('random.random') as mock_random:
        mock_random.return_value = 0.4

        new_date = transformation.transform(date)

    assert new_date == expected
    assert transformation.get_transformed_date() is not None


def test_not_date():
    transformation = DateTransformation()

    transformed = transformation.transform("email")

    assert transformed == '<DATE>'
    assert transformation.get_transformed_date() is None
