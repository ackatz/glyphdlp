import pytest
import re
from .. import regex


# Tax ID Tests
@pytest.mark.parametrize(
    "input_str",
    [
        "TIN# 12-3456789",
        "Tax ID Number 12-3456789",
        "TIN#12-3456789",
        "Tax ID Number#12-3456789",
        "12-3456789",  # plain Tax ID without descriptor
    ],
)
def test_taxid_positive(input_str):
    assert re.search(regex.patterns["tax_id"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "TIN 123-45678",  # not a valid format
        "Tax ID Number#12-34567890",  # too many numbers after dash
        "Tax# 12-345678",  # not a valid descriptor
        "Tax ID Number# ",  # missing Tax ID number
        "TIN #",  # another case with missing number after space
    ],
)
def test_taxid_negative(input_str):
    assert not re.search(regex.patterns["tax_id"], input_str)
