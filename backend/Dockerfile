
# ============================================================
# BASE STAGE - Python and application dependencies
# ============================================================

FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install backend dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source code
COPY app ./app


# ============================================================
# RUNTIME STAGE - Run FastAPI
# ============================================================

FROM base AS runtime

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "app.main:app", \
     "--host", "0.0.0.0", "--port", "8000"]


# ============================================================
# TEST STAGE - Run Unit Tests with Pytest
# ============================================================

FROM base AS test

# Install testing dependencies
COPY requirements-dev.txt ./
RUN pip install --no-cache-dir -r requirements-dev.txt

# Copy Unit Tests
COPY tests ./tests

# Run all tests
CMD ["python", "-m", "pytest", "tests/", "-v"]
