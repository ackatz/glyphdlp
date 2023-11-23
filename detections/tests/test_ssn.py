import pytest
import re
from .. import regex

# SSN Tests


@pytest.mark.parametrize(
    "input_str", ["My SSN is 123-45-6789", "SSN: 234-56-7890", "345-21-4293"]
)
def test_ssn_positive(input_str):
    assert re.search(regex.patterns["ssn"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "My number is 123-45678",
        "Invalid SSN: 12345-6789",
        "123-45-678",
    ],
)
def test_ssn_negative(input_str):
    assert not re.search(regex.patterns["ssn"], input_str)
