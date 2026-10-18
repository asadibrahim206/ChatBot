from chatbot.bot import get_reply


def test_hello_gets_greeting():
    assert get_reply("hello") == "Hi there! How can I help you?"

def test_input_is_cleaned_before_matching():
    assert get_reply("  HELLO  ") == "Hi there! How can I help you?"


def test_unknown_input_gets_fallback():
    assert get_reply("what is the weather") == "Sorry, I don't understand that yet."

def test_bye_gets_goodbye():
    assert get_reply("bye") == "Goodbye! Have a great day."

def test_hello_inside_a_sentence_gets_greeting():
    assert get_reply("hello bot") == "Hi there! How can I help you?"

def test_word_containing_hello_is_not_a_greeting():
    assert get_reply("othello") == "Sorry, I don't understand that yet."

def test_hello_with_punctuation_gets_greeting():
    assert get_reply("Hello!") == "Hi there! How can I help you?"

def test_how_are_you_gets_reply():
    assert get_reply("How are you?") == "I'm just code, but I'm running great!"

def test_two_keywords_get_both_replies():
    reply = get_reply("Hello, how are you?")
    assert "Hi there! How can I help you?" in reply
    assert "I'm just code, but I'm running great!" in reply

def test_bot_remembers_last_user_message():
    history = [
        {"role": "user", "text": "hello"},
        {"role": "bot", "text": "Hi there! How can I help you?"},
    ]
    assert get_reply("What did I say?", history) == 'You said: "hello"'


def test_bot_with_no_history_says_nothing_yet():
    assert get_reply("what did I say?") == "You haven't said anything yet."