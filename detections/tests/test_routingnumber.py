import pytest
import re
from .. import regex


# Routing Number Tests
@pytest.mark.parametrize(
    "input_str",
    [
        "routing# 123456789",
        "routing 123456789",
        "routing#123456789",
    ],
)
def test_routingnumber_positive(input_str):
    assert re.search(regex.patterns["routing_number"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "route 12345678",  # only 8 digits
        "routing#12345678a",  # includes a letter
        "routing# ",  # missing routing number
        "routing #",  # another case with missing number after space
        "123456789",  # plain routing number without descriptor
    ],
)
def test_routingnumber_negative(input_str):
    assert not re.search(regex.patterns["routing_number"], input_str)
