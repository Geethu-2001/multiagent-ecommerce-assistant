import pytest
from multiagent.tools.web_security import validate_public_url, UnsafeURLError

def test_rejects_localhost():
    with pytest.raises(UnsafeURLError):
        validate_public_url("http://localhost:8000/secret")

def test_rejects_non_http():
    with pytest.raises(UnsafeURLError):
        validate_public_url("file:///etc/passwd")

def test_requires_url():
    with pytest.raises(UnsafeURLError):
        validate_public_url("not-a-url")
