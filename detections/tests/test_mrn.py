import pytest
import re
from .. import regex

# MRN tests


# Positive tests
@pytest.mark.parametrize(
    "input_str", ["MRN 12345678", "MRN#123456789", "MRN 1234567890", "MRN# 12345678"]
)
def test_medicalrecordnumber_positive(input_str):
    assert re.search(regex.patterns["medical_record_number"], input_str)


# Negative tests
@pytest.mark.parametrize(
    "input_str",
    [
        "MRN1234567",  # Less than 8 digits
        "MRN 12345678901",  # More than 10 digits
        "MNR 12345678",  # Incorrect abbreviation
        "MRN#ABC12345678",  # Includes letters
        "MRN# 123 456 78",  # Space within the number
    ],
)
def test_medicalrecordnumber_negative(input_str):
    assert not re.search(regex.patterns["medical_record_number"], input_str)
