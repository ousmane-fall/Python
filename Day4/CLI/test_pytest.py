import subprocess
import pytest
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

@pytest.mark.parametrize("name, expected", [
    ("Alice", "Hello, Alice!"),
    ("Bob", "Hello, Bob!")
])
def test_greet_cli(name, expected):
    result = subprocess.run(
        [sys.executable, "cli_tool.py", name],
        capture_output=True,
        text=True,
        cwd=BASE_DIR,
    )
    assert result.stdout.strip() == expected