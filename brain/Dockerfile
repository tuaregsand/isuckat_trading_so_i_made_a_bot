FROM python:3.9-slim
WORKDIR /app

# Install system dependencies for psycopg2
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy dependency definition files
COPY pyproject.toml poetry.lock* /app/

# Install Poetry and dependencies
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --without dev --no-root -vvv

# Copy app source code
COPY . /app

# Expose port and run
EXPOSE 8000
CMD ["uvicorn", "brain:app", "--host", "0.0.0.0", "--port", "8000"]