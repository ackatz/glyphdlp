import pytest
import re
from .. import regex

# Credit Card Tests


@pytest.mark.parametrize(
    "input_str",
    [
        "My Credit Card # is 1234-5678-1234-5678",
        "Card: 2345-6789-9876-5432",
        "3456-7890-8765-4321",
    ],
)
def test_creditcard_positive(input_str):
    assert re.search(regex.patterns["credit_card"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "My card is 1234-5678-1234",
        "Invalid: 1234-5678-9012-345",
        "1234-5678-1234-56789",
    ],
)
def test_creditcard_negative(input_str):
    assert not re.search(regex.patterns["credit_card"], input_str)
