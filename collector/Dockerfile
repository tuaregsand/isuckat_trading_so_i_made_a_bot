FROM python:3.9-slim
WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends ca-certificates gcc libpq-dev && \
    update-ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Copy dependency definition files
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and project dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-root -vvv

# Copy application code
COPY . /app

# Run the collector service
CMD ["python", "collector.py"]