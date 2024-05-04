from datetime import datetime
from unittest.mock import patch

import pytest
from freezegun import freeze_time

from transformations.passport_transformation import PassportTransformation


@pytest.fixture
def prepared_transformation():
    transformation = PassportTransformation(None)
    transformation._year_delta = 2

    return transformation


@freeze_time("2024-06-01")
@pytest.mark.parametrize('transformed_date, series_year', [
    (datetime(2011, 1, 1), '25'),  # 13 лет
    (datetime(2009, 1, 1), '23'),  # 15 лет
    (datetime(2005, 1, 1), '19'),  # 19 лет
    (datetime(2003, 1, 1), '23'),  # 21 лет
    (datetime(1980, 1, 1), '00'),  # 44 года
    (datetime(1978, 1, 1), '23'),  # 46 лет
])
def test_passport_transformation_with_transformed_date(prepared_transformation, transformed_date: datetime, series_year: str):
    prepared_transformation._transformed_date = transformed_date

    transformed = prepared_transformation.transform('1234 567890')

    assert transformed[:4] == f'12{series_year}'
    assert transformed[5:] != '567890'


def test_passport_transformation_without_transformed_date(prepared_transformation):
    with patch('random.randint') as mock_randint:
        mock_randint.side_effect = [20, 198765]
        transformed = prepared_transformation.transform('1234 567890')

    assert transformed == '1220 198765'


def test_not_passport(prepared_transformation):
    transformed = prepared_transformation.transform('test')

    assert transformed == 'test'
