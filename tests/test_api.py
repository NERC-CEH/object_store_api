"""
Minimum possible tests for Object Store API

Not got into detail of mocking components and responses -
is there much value or do we end up testing FastAPI?

At level of "do endpoints exist, and resolve"
"""
import os
from os_api.api import app
import pytest
from fastapi.testclient import TestClient
from moto.server import ThreadedMotoServer
import logging

logging.basicConfig(level=logging.INFO)


@pytest.fixture(scope="module")
def moto_server():
    """Fixture to run a mocked AWS server for testing."""
    # Note: pass `port=0` to get a random free port.
    server = ThreadedMotoServer(port=0)
    server.start()
    host, port = server.get_host_and_port()
    os.environ["AWS_URL_ENDPOINT"] = f"http://{host}:{port}"
    yield f"http://{host}:{port}"
    server.stop()


client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


@pytest.mark.asyncio
def test_create_bucket(moto_server):
    params = {"bucket_name": "test_bucket"}
    response = client.post("/create-bucket/", params=params)
    assert response.status_code == 200


def test_generate_presigned_url(moto_server):
    params = {"filename": "demo.txt", "file_type": "text/plain"}
    response = client.post("/generate-presigned-url/", data=params)
    assert response.status_code == 200


def test_upload():

    response = client.post("/upload/")
    assert response


def test_check_file_exist():

    response = client.post("/check-file-exist/")
    assert response
