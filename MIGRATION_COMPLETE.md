# ✅ Migration from Kafka to Pub/Sub Complete!

## What Was Changed

### Files Deleted ❌
- `src/clients/kafka_config.py` - Kafka configuration
- `src/simulator/producer.py` - Kafka producer
- `src/scripts/test_kafka_connection.py` - Kafka diagnostics
- `src/scripts/test_network.py` - Network diagnostics

### Files Created ✅
- `src/clients/pubsub_config.py` - Pub/Sub configuration
- `src/simulator/publisher.py` - Pub/Sub publisher
- `GCP_SETUP.md` - Complete infrastructure guide
- `deploy_all.sh` - One-command deployment
- `cleanup_kafka.sh` - Kafka cleanup script

### Files Updated 🔄
- `requirements.txt` - Replaced `confluent-kafka` with `google-cloud-pubsub`
- `src/simulator/data_streamer.py` - Uses Pub/Sub publisher
- `src/matchmaking/consumer.py` - Uses Pub/Sub subscriber
- `Dockerfile` - Simplified (no Kafka deps)
- `.env` - New Pub/Sub configuration
- `deploy_streamer.sh` - Updated to use GCR
- `deploy_consumer.sh` - Updated to use GCR
- `README.md` - Updated documentation

---

## 🚀 Quick Start Guide

### 1. Clean Up Kafka (Run Once)

```bash
./cleanup_kafka.sh
```

This will delete:
- Managed Kafka cluster
- VPC connectors
- Firewall rules
- Local Kafka packages

### 2. Setup Pub/Sub Infrastructure

```bash
# Enable APIs
gcloud services enable pubsub.googleapis.com run.googleapis.com

# Create Pub/Sub topic and subscription
gcloud pubsub topics create matchmaking-queue
gcloud pubsub subscriptions create matchmaking-subscription \
  --topic=matchmaking-queue \
  --ack-deadline=60

# Create service account
gcloud iam service-accounts create matchmaking-sa

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

### 3. Deploy Everything

```bash
./deploy_all.sh
```

### 4. Monitor

```bash
# Streamer logs
gcloud run services logs tail streamer --region=europe-west10

# Consumer logs
gcloud run services logs tail consumer --region=europe-west10

# Check Pub/Sub metrics
gcloud pubsub topics describe matchmaking-queue
gcloud pubsub subscriptions describe matchmaking-subscription
```

---

## Architecture Comparison

### Before (Kafka) ❌
```
Cloud Run → VPC Connector → Firewall Rules → Managed Kafka
```
**Issues:**
- Complex networking (VPC, DNS, firewall)
- No DNS zone configured
- Connection failures
- Hard to debug

### After (Pub/Sub) ✅
```
Cloud Run → Pub/Sub
```
**Benefits:**
- Native Cloud Run integration
- No networking configuration
- Automatic credential management
- Easy monitoring in GCP Console

---

## Cost Comparison

### Kafka Monthly Costs
- Managed Kafka cluster: ~$100-200/month (minimum)
- VPC connector: ~$10/month
- **Total: ~$110-210/month**

### Pub/Sub Monthly Costs
- First 10 GB: FREE
- Beyond: $0.40 per million messages
- **Total: ~$0-5/month for light usage**

**💰 Savings: ~$100-200/month!**

---

## Troubleshooting

### Test Pub/Sub Manually

```bash
# Publish a test message
gcloud pubsub topics publish matchmaking-queue \
  --message='{"user_id": 123, "mmr": 1500, "region": "NA"}'

# Pull messages from subscription
gcloud pubsub subscriptions pull matchmaking-subscription --limit=5
```

### Check Service Account Permissions

```bash
gcloud projects get-iam-policy game-lobby-simulation \
  --flatten="bindings[].members" \
  --filter="bindings.members:matchmaking-sa@*"
```

### View Pub/Sub Metrics

Go to: **GCP Console → Pub/Sub → Topics → matchmaking-queue**
- Messages published/sec
- Message backlog
- Oldest unacked message age

---

## Next Steps

1. ✅ All Kafka code removed
2. ✅ Pub/Sub integration complete
3. ✅ Deployment scripts updated
4. ⏭️ Run `./cleanup_kafka.sh`
5. ⏭️ Setup Pub/Sub (see section 2 above)
6. ⏭️ Deploy with `./deploy_all.sh`
7. ⏭️ Monitor logs to verify it works

---

## Need Help?

- **Setup Guide**: See `GCP_SETUP.md`
- **Architecture**: See `README.md`
- **Logs**: `gcloud run services logs tail <service> --region=europe-west10`
- **Pub/Sub Console**: https://console.cloud.google.com/cloudpubsub

🎉 **You're ready to deploy!**
