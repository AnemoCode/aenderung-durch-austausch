from cryptography.fernet import Fernet, InvalidToken
from django.conf import settings
from django.db import models


def _fernet() -> Fernet:
    return Fernet(settings.FIELD_ENCRYPTION_KEY)


class EncryptedTextField(models.TextField):
    """
    A TextField that transparently encrypts its value before writing to the
    database and decrypts it when reading back.

    Encryption uses Fernet symmetric authenticated encryption (AES-128-CBC +
    HMAC-SHA256).  The key is read from ``settings.FIELD_ENCRYPTION_KEY``.

    Important notes
    ---------------
    - Encrypted values are *not* searchable via the ORM (filter/order).
    - Changing ``FIELD_ENCRYPTION_KEY`` after data has been stored will
      make existing values unreadable; plan a re-encryption migration first.
    """

    def from_db_value(self, value, expression, connection):
        if not value:
            return value
        try:
            return _fernet().decrypt(value.encode()).decode()
        except InvalidToken:
            # Return None rather than crashing if a value can't be decrypted
            # (e.g. after a key rotation without migration).
            return None

    def get_prep_value(self, value):
        if not value:
            return value
        return _fernet().encrypt(value.encode()).decode()
