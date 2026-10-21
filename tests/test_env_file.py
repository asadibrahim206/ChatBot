from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_env_file_is_git_ignored():
    lines = (ROOT / ".gitignore").read_text().splitlines()
    assert ".env" in [line.strip() for line in lines]


def test_env_example_lists_the_key_but_holds_no_real_one():
    text = (ROOT / ".env.example").read_text()
    assert "GOOGLE_API_KEY=" in text
    assert "your-key-here" in text