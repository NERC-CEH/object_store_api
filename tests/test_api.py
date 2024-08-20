"""
Minimum possible tests for Object Store API

Not got into detail of mocking components and responses -
is there much value or do we end up testing FastAPI?

At level of "do endpoints exist, and resolve"
"""

from os_api.api import app
from fastapi import FastAPI
from fastapi.testclient import TestClient

# TODO resolve how moto should work with aioboto3 Session + fastapi dependency overrides


client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


# @pytest.mark.asyncio  # TODO see above, mock bucket
def test_create_bucket():
    params = {'bucket_name': 'test_bucket'}
    response = client.post('create_bucket', params=params)
    assert response


def test_generate_presigned_url():

    response = client.post('/generate-presigned-url/')
    assert response

def test_upload():

    response = client.post('/upload/')
    assert response

def test_check_file_exist():

    response = client.post('/check-file-exist/')
    assert response

def test_import_api_module():
    import os_api.api
