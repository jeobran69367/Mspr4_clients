from datetime import datetime

from app.utils.formatters import (
    format_phone_number,
    format_siret,
    format_date,
    format_customer_name,
)


def test_format_phone_number_plain():
    assert format_phone_number("0123456789") == "01 23 45 67 89"


def test_format_phone_number_plus33():
    assert format_phone_number("33123456789") == "+33 1 23 45 67 89"


def test_format_siret():
    assert format_siret("73282932000074") == "732 829 320 00074"
    assert format_siret("invalid") == "invalid"


def test_format_date_and_customer_name():
    d = datetime(2020, 1, 2, 15, 30, 45)
    assert format_date(d, "%Y-%m-%d") == "2020-01-02"
    assert format_date(None) is None
    assert format_customer_name("Mme", "Jean", "Dupont") == "Mme Jean Dupont"
