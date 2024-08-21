"""
Minimum possible tests for Object Store API

Not got into detail of mocking components and responses -
is there much value or do we end up testing FastAPI?

At level of "do endpoints exist, and resolve"
"""
import os
from os_api.api import app, boto_session, s3_endpoint
import pytest
import aioboto3
from fastapi import FastAPI
from fastapi.testclient import TestClient
from moto import mock_aws
import logging
logging.basicConfig(level=logging.INFO)
# TODO resolve how moto should work with aioboto3 Session + fastapi dependency overrides

from moto.server import ThreadedMotoServer

@pytest.fixture(scope="module")
def moto_server():
    """Fixture to run a mocked AWS server for testing."""
    # Note: pass `port=0` to get a random free port.
    server = ThreadedMotoServer(port=0)
    server.start()
    host, port = server.get_host_and_port()
    os.environ['AWS_URL_ENDPOINT'] = f"http://{host}:{port}"
    yield f"http://{host}:{port}"
    server.stop()

# Without both the dependency override _and_ the environment variable set in the fixture,
# the endpoint URL doesn't get set for the API properly - wish i fully understood why! - JW
app.dependency_overrides[s3_endpoint] = moto_server

client = TestClient(app)

def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_create_bucket(moto_server):
    params = {'bucket_name': 'test_bucket'}
    response = client.post('/create-bucket/', params=params)
    assert response.status_code == 200
    print(response.content)


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
