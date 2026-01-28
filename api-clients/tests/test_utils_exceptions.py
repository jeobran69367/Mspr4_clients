from fastapi import status

from app.utils.exceptions import (
    CustomerNotFoundException,
    AddressNotFoundException,
    DuplicateEmailException,
    DuplicateSIRETException,
    InvalidCredentialsException,
    InsufficientPermissionsException,
)


def test_exceptions_details():
    e1 = CustomerNotFoundException("abc")
    assert e1.status_code == status.HTTP_404_NOT_FOUND
    assert "abc" in e1.detail

    e2 = AddressNotFoundException("addr")
    assert e2.status_code == status.HTTP_404_NOT_FOUND
    assert "addr" in e2.detail

    e3 = DuplicateEmailException()
    assert e3.status_code == status.HTTP_400_BAD_REQUEST

    e4 = DuplicateSIRETException()
    assert e4.status_code == status.HTTP_400_BAD_REQUEST

    e5 = InvalidCredentialsException()
    assert e5.status_code == status.HTTP_401_UNAUTHORIZED
    assert "WWW-Authenticate" in e5.headers

    e6 = InsufficientPermissionsException()
    assert e6.status_code == status.HTTP_403_FORBIDDEN
