"""
Minimum possible tests for Object Store API

Not got into detail of mocking components and responses -
is there much value or do we end up testing FastAPI?

At level of "do endpoints exist, and resolve"
"""

import os
from os_api.api import app, s3_endpoint
import pytest
import aioboto3
from fastapi import FastAPI
from fastapi.testclient import TestClient
from moto import mock_aws
import logging

logging.basicConfig(level=logging.INFO)

from moto.server import ThreadedMotoServer


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


# Without both the dependency override _and_ the environment variable set in the fixture,
# the endpoint URL doesn't get set for the API properly - wish i fully understood why! - JW
app.dependency_overrides[s3_endpoint] = moto_server

client = TestClient(app)


def test_read_main():
    response = client.get("/")
    assert response.status_code == 200


def test_create_bucket(moto_server):
    params = {"bucket_name": "test_bucket"}
    response = client.post("/create-bucket/", params=params)
    assert response.status_code == 200


def test_generate_presigned_url(moto_server):
    params = {
        "filename": "demo.txt",
        "file_type": "text/plain",
        "bucket_name": "test_bucket",
    }
    response = client.post("/generate-presigned-url/", data=params)
    assert response.status_code == 200


def test_upload(text_file):
    data = {"bucket_name": "test_bucket"}
    response = client.post("/create-bucket/", params=data)
    response = client.post("/upload/", data=data, files=[("files", text_file)])
    assert response.status_code == 200


def test_check_file_exist(text_file):
    data = {"bucket_name": "test_bucket"}
    response = client.post("/create-bucket/", params=data)
    response = client.post("/upload/", data=data, files=[("files", text_file)])
    data["filename"] = "1_test.txt"
    response = client.post("/check-file-exist/", data=data)
    assert response.status_code == 200


def test_list_buckets():
    buckets = ["hello", "world"]
    for b in buckets:
        client.post("/create-bucket/", params={"bucket_name": b})
    res = client.get("/list-buckets/")
    bucket_list = res.json()
    for b in buckets:
        assert b in bucket_list


def test_import_api_module():
    import os_api.api
