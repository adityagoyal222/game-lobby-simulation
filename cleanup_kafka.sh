#!/bin/bash
# Script to clean up all Kafka-related infrastructure from GCP

PROJECT_ID="game-lobby-simulation"
REGION="europe-west10"

echo "🧹 Cleaning up Kafka infrastructure..."
echo ""

# Delete Kafka cluster
echo "Deleting Managed Kafka cluster..."
gcloud managed-kafka clusters delete kafka-matchmaking \
  --location=$REGION \
  --quiet 2>/dev/null && echo "✅ Kafka cluster deleted" || echo "⚠️  No Kafka cluster found"
echo ""

# Delete VPC connector
echo "Deleting VPC connector..."
gcloud compute networks vpc-access connectors list --region=$REGION --format="value(name)" | while read connector; do
  echo "  Deleting: $connector"
  gcloud compute networks vpc-access connectors delete $connector \
    --region=$REGION \
    --quiet 2>/dev/null
done
echo "✅ VPC connectors deleted"
echo ""

# Delete firewall rules
echo "Deleting firewall rules..."
for rule in allow-kafka-egress allow-kafka-ingress; do
  gcloud compute firewall-rules delete $rule \
    --quiet 2>/dev/null && echo "  ✅ Deleted: $rule" || echo "  ⚠️  Not found: $rule"
done
echo ""

# Clean up local Kafka files
echo "Removing local Kafka Python packages..."
if [ -d "venv" ]; then
  source venv/bin/activate 2>/dev/null || true
  pip uninstall -y confluent-kafka kafka-python 2>/dev/null || true
  deactivate 2>/dev/null || true
fi
echo "✅ Local packages cleaned"
echo ""

echo "🎉 Kafka cleanup complete!"
echo ""
echo "Next steps:"
echo "  1. Run: ./deploy_all.sh"
echo "  2. Check GCP Console to verify Pub/Sub resources exist"
