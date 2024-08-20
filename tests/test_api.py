from os_api.api import app
from fastapi import FastAPI
from fastapi.testclient import TestClient


client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_create_bucket():

    response = client.post('create_bucket')
    print(response.content)


def test_generate_presigned_url():

    response = client.post('/generate-presigned-url/')


def test_upload():

    response = client.post('/upload/')

def test_check_file_exist():

    response = client.post('/check-file-exist/')

def test_import_api_module():
    import os_api.api

