import pytest
import re
from .. import regex

# ID # tests


@pytest.mark.parametrize(
    "input_str",
    ["DL# 123456", "TX 12345678", "Driver's License 9876-5432", "NY 12345678"],
)
def test_id_positive(input_str):
    assert re.search(regex.patterns["id_or_passport"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "Driving License 1234 5678",
        "DL12345",
        "TX-",
        "Driver'sLicence 12345678",
        "Driving Licence#",
        "ABC 1234",
        "Drive License 1234-5678",
        "DLABC-1234567",
        "Driving License#123456789012345",  # more than 15 numbers
    ],
)
def test_id_negative(input_str):
    assert not re.search(regex.patterns["id_or_passport"], input_str)


# Passport Tests
@pytest.mark.parametrize(
    "input_str",
    [
        "US Passport 1234567",
        "Passport 1234567",
        "USPassport 12345678",
        "US Passport # 123456789",
        "US Passport#1234567890",
        "Passport#1234567890",
    ],
)
def test_passport_positive(input_str):
    assert re.search(regex.patterns["id_or_passport"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "US Passport D1234567",  # Numbers prefixed by a letter other than '#'
        "US Passport 123456",  # Less than 7 digits
        "Passport 123456",  # Less than 7 digits without "US"
        "US Passport 12345678901",  # More than 10 digits
        "USPassport# ABCDEFGH",  # Letters after '#'
        "Passport# ABCDEFGH",  # Letters after '#', without "US"
    ],
)
def test_passport_negative(input_str):
    assert not re.search(regex.patterns["id_or_passport"], input_str)
