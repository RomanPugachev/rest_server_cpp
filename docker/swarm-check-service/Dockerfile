FROM python:3.12.5-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY ./src/main/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY ./src/main/ .

ENTRYPOINT ["python", "MainClientChecker.py"]