from moto import mock_aws
import pytest
import aioboto3


@pytest.fixture
async def mock_s3_client():
    with mock_aws():
        session = aioboto3.Session(region_name="us-east-1")
        async with session.client("s3", region_name="us-east-1") as client:  # type: S3Client
            yield client


