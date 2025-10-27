import pytest
from vcc_urn.security import extract_roles_from_claims


def test_extract_roles_from_roles_list():
    claims = {"roles": ["admin", "user"]}
    assert extract_roles_from_claims(claims) == ["admin", "user"]


def test_extract_roles_from_roles_string():
    claims = {"roles": "admin,user"}
    assert extract_roles_from_claims(claims) == ["admin", "user"]


def test_extract_roles_from_groups():
    claims = {"groups": ["group1", "group2"]}
    assert extract_roles_from_claims(claims) == ["group1", "group2"]


def test_extract_roles_from_scope():
    claims = {"scope": "read write admin"}
    assert extract_roles_from_claims(claims) == ["read", "write", "admin"]


def test_extract_roles_from_realm_access():
    claims = {"realm_access": {"roles": ["realm-admin"]}}
    assert extract_roles_from_claims(claims) == ["realm-admin"]


def test_extract_roles_empty():
    claims = {"sub": "u1"}
    assert extract_roles_from_claims(claims) == []
