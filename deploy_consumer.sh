#!/bin/bash
set -e

DOCKER_USERNAME="kemonache"

echo "🚀 Building and pushing consumer..."

# Clean cache
find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true

# Build and push
VERSION=$(date +%s)
docker build --no-cache --platform linux/amd64 --target consumer \
  -t $DOCKER_USERNAME/consumer:v$VERSION \
  -t $DOCKER_USERNAME/consumer:latest .

docker push $DOCKER_USERNAME/consumer:v$VERSION
docker push $DOCKER_USERNAME/consumer:latest

echo "✅ Consumer image pushed:"
echo "   docker.io/$DOCKER_USERNAME/consumer:v$VERSION"
echo "   docker.io/$DOCKER_USERNAME/consumer:latest"