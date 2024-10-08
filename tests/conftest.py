import os
import pytest


@pytest.fixture
def fixture_dir():
    """
    Base directory for the test fixtures (images, metadata)
    """
    return os.path.join(os.path.abspath(os.path.dirname(__file__)), "fixtures/")


@pytest.fixture
def text_file(fixture_dir):
    """
    Sample text file
    """
    return open(os.path.join(fixture_dir, "1_test.txt"), "rb")
