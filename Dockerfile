FROM --platform=linux/amd64 python:3.11-slim as base

WORKDIR /app
COPY setup.py .
COPY requirements.txt .
COPY .env /app/.env

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Build streamer
FROM base as streamer
COPY . .
RUN pip install --no-cache-dir -e .
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "\
    python -m http.server 8080 --bind 0.0.0.0 2>&1 > /dev/null & \
    python -u src/scripts/init_db.py && \
    python -u src/scripts/data_gen.py --players 500 && \
    exec python -u src/simulator/data_streamer.py"]

# Build consumer
FROM base as consumer
COPY . .
RUN pip install --no-cache-dir -e .
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
CMD ["sh", "-c", "\
    python -m http.server 8080 --bind 0.0.0.0 2>&1 > /dev/null & \
    python -u src/scripts/init_db.py || true && \
    exec python -u src/matchmaking/consumer.py"]