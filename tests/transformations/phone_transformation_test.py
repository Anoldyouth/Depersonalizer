from unittest.mock import patch

import pytest

from transformations.phone_transformation import PhoneTransformation


@pytest.mark.parametrize('phone,expected', [
    ('81234567890', '81239876540'),
    ('+71234567890', '+71239876540'),
    ('8(123)456-78-90', '8(123)987-65-40')
])
def test_phone_transformed(phone, expected):
    transformation = PhoneTransformation()
    with patch('random.randint') as mock_randint:
        mock_randint.side_effect = [
            987, 65, 40
        ]

        new_phone = transformation.transform(phone)

    assert new_phone != phone
    assert new_phone == expected


def test_not_phone():
    transformation = PhoneTransformation()

    transformed = transformation.transform("test")

    assert transformed == '<PHONE>'
