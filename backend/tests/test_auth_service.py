"""
backend/tests/test_auth_service.py
"""

from backend.services.auth_service import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
import uuid


def test_password_hash_roundtrip():
    hashed = hash_password("password123")
    assert hashed != "password123"
    assert verify_password("password123", hashed)
    assert not verify_password("wrong", hashed)


def test_jwt_roundtrip():
    uid = uuid.uuid4()
    tid = uuid.uuid4()
    token = create_access_token(
        user_id=uid, tenant_id=tid, role="student", email="a@b.com"
    )
    payload = decode_access_token(token)
    assert payload["sub"] == str(uid)
    assert payload["tenant_id"] == str(tid)
    assert payload["role"] == "student"
