import pytest


def test_fallo_intencionado():
    pytest.fail("Fallo intencionado para comprobar que el CI detecta errores")