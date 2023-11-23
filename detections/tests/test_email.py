import pytest
import re
from .. import regex

# Email Address Tests


@pytest.mark.parametrize(
    "input_str",
    [
        "email@example.com",
        "first.last@example.co.uk",
        "user.name+tag+sorting@example.com",
        "x@example.com",
        "123.456@example.ac.in",
    ],
)
def test_emailaddress_positive(input_str):
    assert re.search(regex.patterns["email_address"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "plainaddress",
        "@missingusername.com",
        "username@.com",
        "username@server.",
        "username@server",
    ],
)
def test_emailaddress_negative(input_str):
    assert not re.search(regex.patterns["email_address"], input_str)
