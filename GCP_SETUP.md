# GCP Setup Guide for Matchmaking System with Pub/Sub

This guide walks you through setting up the entire infrastructure from scratch.

## Prerequisites

- GCP Project: `game-lobby-simulation`
- Region: `europe-west10`
- gcloud CLI installed and authenticated

## Step 1: Clean Up Old Resources (If Any)

```bash
# Delete old Kafka cluster (if exists)
gcloud managed-kafka clusters delete kafka-matchmaking \
  --location=europe-west10 --quiet || true

# Delete VPC connector (if exists)
gcloud compute networks vpc-access connectors delete YOUR_CONNECTOR_NAME \
  --region=europe-west10 --quiet || true

# Delete firewall rules
gcloud compute firewall-rules delete allow-kafka-egress --quiet || true
gcloud compute firewall-rules delete allow-kafka-ingress --quiet || true
```

## Step 2: Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  sqladmin.googleapis.com \
  pubsub.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com
```

## Step 3: Create Cloud SQL Database

```bash
# Create Cloud SQL instance (if not exists)
gcloud sql instances create db-matchmaking \
  --database-version=POSTGRES_15 \
  --tier=db-f1-micro \
  --region=europe-west10 \
  --network=default \
  --no-assign-ip

# Get the private IP
gcloud sql instances describe db-matchmaking \
  --format="value(ipAddresses[0].ipAddress)"
# Update this IP in your .env file as DB_HOST

# Create database
gcloud sql databases create matchmaking_db \
  --instance=db-matchmaking

# Set password
gcloud sql users set-password postgres \
  --instance=db-matchmaking \
  --password=postgres
```

## Step 4: Create Pub/Sub Topic and Subscription

```bash
# Create topic
gcloud pubsub topics create matchmaking-queue

# Create subscription
gcloud pubsub subscriptions create matchmaking-subscription \
  --topic=matchmaking-queue \
  --ack-deadline=60 \
  --message-retention-duration=7d
```

## Step 5: Create Service Account with Permissions

```bash
# Create service account
gcloud iam service-accounts create matchmaking-sa \
  --display-name="Matchmaking Service Account"

# Grant permissions
gcloud projects add-iam-policy-binding game-lobby-simulation \
  --member="serviceAccount:matchmaking-sa@game-lobby-simulation.iam.gserviceaccount.com" \
  --role="roles/pubsub.publisher"

gcloud projects add-iam-policy-binding game-lobby-simulation \
  --member="serviceAccount:matchmaking-sa@game-lobby-simulation.iam.gserviceaccount.com" \
  --role="roles/pubsub.subscriber"

gcloud projects add-iam-policy-binding game-lobby-simulation \
  --member="serviceAccount:matchmaking-sa@game-lobby-simulation.iam.gserviceaccount.com" \
  --role="roles/cloudsql.client"
```

## Step 6: Build and Push Docker Images

```bash
# Build streamer
docker build --platform linux/amd64 --target streamer \
  -t gcr.io/game-lobby-simulation/streamer:latest .

docker push gcr.io/game-lobby-simulation/streamer:latest

# Build consumer
docker build --platform linux/amd64 --target consumer \
  -t gcr.io/game-lobby-simulation/consumer:latest .

docker push gcr.io/game-lobby-simulation/consumer:latest
```

## Step 7: Deploy Cloud Run Services

### Deploy Streamer

```bash
gcloud run deploy streamer \
  --image=gcr.io/game-lobby-simulation/streamer:latest \
  --region=europe-west10 \
  --platform=managed \
  --service-account=matchmaking-sa@game-lobby-simulation.iam.gserviceaccount.com \
  --add-cloudsql-instances=game-lobby-simulation:europe-west10:db-matchmaking \
  --set-env-vars="GCP_PROJECT_ID=game-lobby-simulation,PUBSUB_TOPIC_ID=matchmaking-queue,INSTANCE_CONNECTION_NAME=game-lobby-simulation:europe-west10:db-matchmaking,DB_NAME=matchmaking_db,DB_USER=postgres,DB_PASSWORD=postgres" \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=1
```

### Deploy Consumer

```bash
gcloud run deploy consumer \
  --image=gcr.io/game-lobby-simulation/consumer:latest \
  --region=europe-west10 \
  --platform=managed \
  --service-account=matchmaking-sa@game-lobby-simulation.iam.gserviceaccount.com \
  --add-cloudsql-instances=game-lobby-simulation:europe-west10:db-matchmaking \
  --set-env-vars="GCP_PROJECT_ID=game-lobby-simulation,PUBSUB_SUBSCRIPTION_ID=matchmaking-subscription,INSTANCE_CONNECTION_NAME=game-lobby-simulation:europe-west10:db-matchmaking,DB_NAME=matchmaking_db,DB_USER=postgres,DB_PASSWORD=postgres" \
  --allow-unauthenticated \
  --memory=512Mi \
  --cpu=1 \
  --min-instances=1 \
  --max-instances=3
```

## Step 8: Verify Everything Works

```bash
# Check streamer logs
gcloud run services logs read streamer --region=europe-west10 --limit=50

# Check consumer logs
gcloud run services logs read consumer --region=europe-west10 --limit=50

# View Pub/Sub messages
gcloud pubsub subscriptions pull matchmaking-subscription --limit=5
```

## Architecture Overview

```
┌─────────────────┐
│   Cloud Run     │
│   (Streamer)    │──► Publishes messages
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Pub/Sub       │
│   Topic/Sub     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Cloud Run     │
│   (Consumer)    │──► Processes matches
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Cloud SQL     │
│   (Postgres)    │
└─────────────────┘
```

## Benefits of This Setup

✅ **No VPC connectors needed** - Pub/Sub works natively
✅ **No DNS configuration** - Fully managed service
✅ **No firewall rules** - Built-in security
✅ **Automatic scaling** - Cloud Run scales to zero
✅ **Simple debugging** - View messages in GCP Console
✅ **Cost effective** - Pay only for what you use

## Costs Estimate

- Cloud SQL (db-f1-micro): ~$7/month
- Pub/Sub: $0.40 per million messages
- Cloud Run: $0.00002400 per vCPU-second
- **Total**: ~$10-15/month for light usage

## Troubleshooting

### Check Pub/Sub has messages
```bash
gcloud pubsub topics describe matchmaking-queue
gcloud pubsub subscriptions describe matchmaking-subscription
```

### Test publishing manually
```bash
gcloud pubsub topics publish matchmaking-queue \
  --message='{"user_id": 123, "mmr": 1500}'
```

### View Cloud Run logs in real-time
```bash
gcloud run services logs tail streamer --region=europe-west10
gcloud run services logs tail consumer --region=europe-west10
```
