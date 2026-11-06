import pytest

from chatbot.errors import EmailAlreadyRegisteredError
from chatbot.user_store import InMemoryUserStore, PostgresUserStore


@pytest.fixture(params=["memory", "postgres"])
def users(request):
    if request.param == "memory":
        yield InMemoryUserStore()
    else:
        store = PostgresUserStore(request.getfixturevalue("migrated_database_url"))
        yield store
        store.close()


def test_created_user_can_be_found_by_email(users):
    created = users.create_user("ali@example.com", "hash-1")

    found = users.get_by_email("ali@example.com")

    assert found == created
    assert found.password_hash == "hash-1"


def test_created_user_can_be_found_by_id(users):
    created = users.create_user("ali@example.com", "hash-1")
    assert users.get_by_id(created.id) == created


def test_unknown_user_is_none(users):
    assert users.get_by_email("nobody@example.com") is None
    assert users.get_by_id(999999) is None


def test_email_is_trimmed_and_lowercased(users):
    created = users.create_user("  Ali@Example.COM ", "hash-1")

    assert created.email == "ali@example.com"
    assert users.get_by_email("ALI@example.com") == created


def test_duplicate_email_is_rejected_even_with_different_case(users):
    users.create_user("ali@example.com", "hash-1")

    with pytest.raises(EmailAlreadyRegisteredError):
        users.create_user("ALI@example.com", "hash-2")


def test_users_get_different_ids(users):
    first = users.create_user("a@example.com", "hash")
    second = users.create_user("b@example.com", "hash")
    assert first.id != second.id


def test_duplicate_email_error_is_a_conflict():
    error = EmailAlreadyRegisteredError()
    assert error.status_code == 409
    assert error.code == "email_already_registered"