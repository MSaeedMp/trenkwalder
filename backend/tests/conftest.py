import os

import pytest

os.environ["APP_ENV"] = "test"
os.environ["DEBUG"] = "false"
os.environ["LOG_LEVEL"] = "WARNING"
os.environ["GEMINI_API_KEY"] = "test-key"


def pytest_configure(config: pytest.Config) -> None:
    config.addinivalue_line("markers", "unit: fast tests, no I/O, mocked boundaries")
    config.addinivalue_line("markers", "integration: real I/O (LanceDB, files, subprocess)")
