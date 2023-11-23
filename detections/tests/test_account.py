import pytest
import re
from .. import regex

# Account Number Tests


@pytest.mark.parametrize(
    "input_str",
    [
        "account 1234567890",
        "account # 123456789012",
        "acct# 123456789012",
        "acct# 12342679012",
    ],
)
def test_bankaccount_positive(input_str):
    assert re.search(regex.patterns["account_number"], input_str)


@pytest.mark.parametrize(
    "input_str",
    [
        "accnt# 1234567890",
        "account#12345678AB",
        "123456789012",  # plain bank account number without descriptor
    ],
)
def test_bankaccount_negative(input_str):
    assert not re.search(regex.patterns["account_number"], input_str)
