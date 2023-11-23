import pytest
import re
from .. import regex

# Medicare Number Tests


# Positive tests
@pytest.mark.parametrize(
    "input_str",
    [
        "Medicare#123-45-6789",
        "Medicare# 123-45-6789",
        "Medicare 123-45-6789",
    ],
)
def test_medicarenumber_positive(input_str):
    assert re.search(regex.patterns["medicare_number"], input_str)


# Negative tests
@pytest.mark.parametrize(
    "input_str",
    [
        "Medicare#1234-56-7890",  # Incorrect number of digits
        "Medicare 123456-7890",  # Incorrect format
        "Medicares# 123-45-6789",  # Typo in "Medicare"
        "Medicare123-45-67890",  # Incorrect number of digits
        "Medicare ABC-45-6789",  # Includes letters
        "Medicare#1234-56-789",  # Incorrect number of digits
        "Medicare 123 45 6789",  # Missing hyphens
    ],
)
def test_medicarenumber_negative(input_str):
    assert not re.search(regex.patterns["medicare_number"], input_str)
