from app.main import _cors_origins


def test_local_dev_cors_origins_include_loopback_hosts():
    origins = _cors_origins()

    assert "http://localhost:3000" in origins
    assert "http://127.0.0.1:3000" in origins
    assert "http://[::1]:3000" in origins
    assert "http://localhost:5173" in origins
    assert "http://127.0.0.1:5173" in origins
    assert "http://[::1]:5173" in origins
