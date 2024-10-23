FROM python:3.12.5-slim

WORKDIR /app

#RUN apt-get update && apt-get install -y \
#    gcc \
#    libpq-dev \
#    && rm -rf /var/lib/apt/lists/* \

RUN apt update && apt install -y curl docker.io
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python", "main.py"]