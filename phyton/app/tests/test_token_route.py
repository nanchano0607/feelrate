import jwt
import pytest

from routes.token import decode_user_id

SECRET = "test-secret-key-that-is-long-enough-32b"


def test_decode_user_id_reads_secret_from_env(monkeypatch):
    # Arrange
    monkeypatch.setenv("JWT_SECRET", SECRET)
    token = jwt.encode({"id": 7, "sub": "user@example.com"}, SECRET, algorithm="HS256")

    # Act
    user_id = decode_user_id(token)

    # Assert
    assert user_id == "7"


def test_decode_user_id_rejects_token_signed_with_other_secret(monkeypatch):
    # Arrange
    monkeypatch.setenv("JWT_SECRET", SECRET)
    forged = jwt.encode({"id": 7}, "attacker-secret-key-that-is-32-bytes!", algorithm="HS256")

    # Act & Assert
    with pytest.raises(jwt.InvalidTokenError):
        decode_user_id(forged)


def test_decode_user_id_requires_secret_env(monkeypatch):
    # Arrange
    monkeypatch.delenv("JWT_SECRET", raising=False)
    token = jwt.encode({"id": 7}, SECRET, algorithm="HS256")

    # Act & Assert
    with pytest.raises(ValueError, match="JWT_SECRET"):
        decode_user_id(token)
