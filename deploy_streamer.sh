#!/bin/bash
set -e

DOCKER_USERNAME="kemonache"

echo "🚀 Building and pushing streamer..."

# Clean cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Build and push
VERSION=$(date +%s)
docker build --no-cache --platform linux/amd64 --target streamer \
  -t $DOCKER_USERNAME/streamer:v$VERSION \
  -t $DOCKER_USERNAME/streamer:latest .

docker push $DOCKER_USERNAME/streamer:v$VERSION
docker push $DOCKER_USERNAME/streamer:latest

echo "✅ Streamer image pushed:"
echo "   docker.io/$DOCKER_USERNAME/streamer:v$VERSION"
echo "   docker.io/$DOCKER_USERNAME/streamer:latest"