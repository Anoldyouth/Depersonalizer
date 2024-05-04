import pytest

from transformations.phone_transformation import PhoneTransformation


@pytest.mark.parametrize('phone,start_from', [
    ('81234567890', '8123'),
    ('+71234567890', '+7123'),
    ('8(123)456-78-90', '8(123)')
])
def test_phone_transformed(phone, start_from):
    transformation = PhoneTransformation()

    new_phone = transformation.transform(phone)

    assert new_phone != phone
    assert new_phone.startswith(start_from)


def test_not_phone():
    transformation = PhoneTransformation()

    transformed = transformation.transform("test")

    assert transformed == '<PHONE>'
