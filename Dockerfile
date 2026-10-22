# Use Python 3.14 because pyproject.toml requires Python >=3.14.
FROM python:3.14-slim

# Keep Python output visible in Azure logs and avoid .pyc files.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv, which is the package manager used by this project.
RUN pip install --no-cache-dir uv

# Copy dependency metadata first to make Docker builds more cache-friendly.
COPY pyproject.toml uv.lock README.md ./
COPY src ./src

# Install the app and production dependencies from the committed lockfile.
RUN uv sync --frozen --no-dev

# Azure Container Apps will route external traffic to this port.
EXPOSE 8080

CMD ["uv", "run", "--frozen", "--no-dev", "uvicorn", "chatbot.main:app", "--host", "0.0.0.0", "--port", "8080"]
