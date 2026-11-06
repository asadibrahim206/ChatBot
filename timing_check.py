import time

from google import genai

from chatbot.config import get_api_key, get_model, load_env

load_env()
client = genai.Client(api_key=get_api_key())

for label in ("first call", "second call"):
    start = time.perf_counter()
    response = client.models.generate_content(
        model=get_model(),
        contents="Say hello in five words.",
    )
    seconds = round(time.perf_counter() - start, 1)
    print(label, seconds, "s |", getattr(response, "model_version", "?"), "|", response.text)