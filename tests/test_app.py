import os
import sys
import pytest

# Ensure project root is importable when tests run from pytest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app as flask_app


@pytest.fixture
def client():
    flask_app.config['TESTING'] = True
    with flask_app.test_client() as client:
        yield client


def test_index(client):
    res = client.get('/')
    assert res.status_code == 200
    assert b'Scamazon' in res.data


def test_product_pages(client):
    # existing product ids are 1,2,3
    for pid in ('1', '2', '3'):
        res = client.get(f'/product/{pid}')
        assert res.status_code == 200
        assert b'Why this is a scam' in res.data
