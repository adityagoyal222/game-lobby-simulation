FROM --platform=linux/amd64 python:3.12.7-slim as base

WORKDIR /app
COPY setup.py .
COPY requirements.txt .
COPY .env .

# Install common dependencies
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Build streamer
FROM base as streamer
ARG SERVICE=streamer
COPY . .
ENV PYTHONPATH=/app
CMD ["sh", "-c", "python src/scripts/init_db.py && python src/scripts/data_gen.py --clean && exec python src/simulator/data_streamer.py"]

# Build consumer  
FROM base as consumer
ARG SERVICE=consumer
COPY . .
ENV PYTHONPATH=/app
CMD ["sh", "-c", "python src/scripts/init_db.py && exec python src/matchmaking/matchmaking_consumer.py"]