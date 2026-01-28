from app.utils.validators import (
    validate_email,
    validate_phone,
    validate_siret,
    validate_postal_code,
    validate_tva_intracommunautaire,
)


def test_validate_email():
    assert validate_email("test@example.com")
    assert not validate_email("bad-email")


def test_validate_phone():
    assert validate_phone("0123456789")
    assert validate_phone("+33123456789")
    assert not validate_phone("123")


def test_validate_siret():
    # build a valid SIRET deterministically using the same checksum logic
    base = "7328293200007"  # 13 digits
    total = 0
    for i, digit in enumerate(base):
        n = int(digit)
        if i % 2 == 1:
            n *= 2
            if n > 9:
                n -= 9
        total += n

    check = None
    # the validator applies the doubling rule on the final digit too depending on its index
    for d in range(10):
        nd = d
        if len(base) % 2 == 1:
            # if base length is odd, the final digit index (which will be len(base)) is odd -> apply doubling
            if (len(base)) % 2 == 1:
                nd = d * 2
                if nd > 9:
                    nd -= 9
        # compute total with candidate check digit processed same way
        if (total + nd) % 10 == 0:
            check = d
            break
    assert check is not None
    valid = base + str(check)
    assert validate_siret(valid)
    assert not validate_siret("00000000000000")


def test_validate_postal_code_and_tva():
    assert validate_postal_code("75001")
    assert not validate_postal_code("75A01")
    assert validate_tva_intracommunautaire("FR40372829309")
    assert not validate_tva_intracommunautaire("INVALID")
