from transformations.email_transformation import EmailTransformation


def test_email_transformed():
    transformation = EmailTransformation()
    email = "email@email.com"

    new_email = transformation.transform("email@email.com")

    assert new_email != email
    assert new_email.endswith('@email.com')


def test_not_email():
    transformation = EmailTransformation()

    transformed = transformation.transform("email")

    assert transformed == 'email'
