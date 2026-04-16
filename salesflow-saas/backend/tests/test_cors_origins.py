from app.main import _cors_origins


def test_cors_origins_include_localhost_aliases():
    origins = _cors_origins()
    assert "http://localhost:3000" in origins
    assert "http://127.0.0.1:3000" in origins
