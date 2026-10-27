from pathlib import Path

ROOT = Path(__file__).parent.parent


def test_env_file_is_git_ignored():
    lines = (ROOT / ".gitignore").read_text().splitlines()
    assert ".env" in [line.strip() for line in lines]


def test_env_example_lists_the_key_but_holds_no_real_one():
    text = (ROOT / ".env.example").read_text()
    assert "GOOGLE_API_KEY=" in text
    assert "your-key-here" in text



def test_compose_file_reads_the_password_from_the_environment():
    text = (ROOT / "docker-compose.yml").read_text()
    assert "${POSTGRES_PASSWORD" in text


def test_env_example_lists_the_database_settings():
    text = (ROOT / ".env.example").read_text()
    assert "POSTGRES_PASSWORD=" in text
    assert "DATABASE_URL=" in text


def test_env_example_database_host_is_not_localhost():
    text = (ROOT / ".env.example").read_text()
    assert "@127.0.0.1:" in text
    assert "@localhost:" not in text