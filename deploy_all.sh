#!/bin/bash
set -e

DOCKER_USERNAME="kemonache"
PROJECT_ID="game-lobby-simulation"
REGION="europe-west10"

echo "🚀 Deploying Matchmaking System to GCP..."
echo ""

# Build and push streamer
echo "📦 Building streamer..."
docker build --platform linux/amd64 --target streamer \
  -t $DOCKER_USERNAME/streamer:latest .
docker push $DOCKER_USERNAME/streamer:latest
echo "✅ Streamer built and pushed"
echo ""

# Build and push consumer
echo "📦 Building consumer..."
docker build --platform linux/amd64 --target consumer \
  -t $DOCKER_USERNAME/consumer:latest .
docker push $DOCKER_USERNAME/consumer:latest
echo "✅ Consumer built and pushed"
echo ""

# Deploy streamer
echo "🚢 Deploying streamer to Cloud Run..."
gcloud run deploy streamer \
  --image=docker.io/$DOCKER_USERNAME/streamer:latest \
  --region=$REGION \
  --platform=managed \
  --service-account=matchmaking-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:db-matchmaking \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,PUBSUB_TOPIC_ID=matchmaking-queue" \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1
echo "✅ Streamer deployed"
echo ""

# Deploy consumer
echo "🚢 Deploying consumer to Cloud Run..."
gcloud run deploy consumer \
  --image=docker.io/$DOCKER_USERNAME/consumer:latest \
  --region=$REGION \
  --platform=managed \
  --service-account=matchmaking-sa@$PROJECT_ID.iam.gserviceaccount.com \
  --add-cloudsql-instances=$PROJECT_ID:$REGION:db-matchmaking \
  --set-env-vars="GCP_PROJECT_ID=$PROJECT_ID,PUBSUB_SUBSCRIPTION_ID=matchmaking-subscription" \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=3
echo "✅ Consumer deployed"
echo ""

echo "🎉 Deployment complete!"
echo ""
echo "View streamer logs:"
echo "  gcloud run services logs tail streamer --region=$REGION"
echo ""
echo "View consumer logs:"
echo "  gcloud run services logs tail consumer --region=$REGION"
