import pytest
import re
from .. import regex


# Date of Birth Tests
@pytest.mark.parametrize(
    "input_str",
    [
        "DOB 01/01/2000",
        "Date of Birth 01/01/2000",
        "DOB 01/01/2000",  # included space for clarity
        "Date of Birth 01/01/2000",  # included space for clarity
        "01/01/2000",  # plain date without descriptor using slash
        "DOB 01-01-2000",  # using dash
        "01-01-2000",  # plain date without descriptor using dash
    ],
)
def test_dob_positive(input_str):
    assert re.search(regex.patterns["date_of_birth"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "DOB 01.01.2000",  # not a valid format (dot used instead of slash or dash)
        "Date of Birth 0101/2000",  # missing slash
        "Date of Birth# 01/01/200",  # year not four digits
        "DOB ",  # missing date after space
    ],
)
def test_dob_negative(input_str):
    assert not re.search(regex.patterns["date_of_birth"], input_str)
