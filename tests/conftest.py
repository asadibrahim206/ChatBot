import os

os.environ["CHATBOT_DB"] = ":memory:"
os.environ["CHATBOT_BRAIN"] = "rules"
os.environ.pop("GOOGLE_API_KEY", None)
os.environ.pop("GEMINI_API_KEY", None)