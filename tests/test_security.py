from chatbot.security import hash_password, verify_password


def test_hash_does_not_contain_the_password():
    assert "correct horse battery" not in hash_password("correct horse battery")


def test_correct_password_verifies():
    hashed = hash_password("correct horse battery")
    assert verify_password("correct horse battery", hashed)


def test_wrong_password_does_not_verify():
    hashed = hash_password("correct horse battery")
    assert not verify_password("wrong password", hashed)


def test_same_password_gives_different_hashes():
    assert hash_password("same password") != hash_password("same password")