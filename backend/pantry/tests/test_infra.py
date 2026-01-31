import pytest

def test_sanity():
    assert 1 == 1

def test_django_setup():
    from django.conf import settings
    assert settings.SECRET_KEY is not None