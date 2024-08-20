from os_api.api import app
from fastapi import FastAPI
from fastapi.testclient import TestClient


client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_import_api_module():
    import os_api.api

