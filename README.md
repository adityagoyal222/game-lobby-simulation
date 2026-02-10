# Game Matchmaking System with Kafka on GCP

A scalable matchmaking system for fighter games (like Tekken) built with Kafka on Google Cloud Platform. Focuses on **Kafka streaming infrastructure** - producer, consumer, and queue management.

**🎯 Ultra Simplified for Demo**: 
- Only **User** data model
- No match history or complex tables
- Your algorithm updates the User table directly
- Pure focus on Kafka + Queue management

See [SIMPLIFIED.md](SIMPLIFIED.md) for what was removed.

## 🏗️ Architecture

**Pure Kafka Streaming Pipeline:**

```
Streaming Data (User logs)
         ↓
    [Kafka Producer] ← Your synthetic data generator streams here
         ↓
    Kafka Topic (matchmaking-queue) ← Message broker on GCP
         ↓
    [Kafka Consumer] + Queue Manager
         ↓
    Matchmaking Algorithm ← Your custom logic plugs in here
         ↓
    Match Created
         ↓
    Game Outcome System ← Can also use Kafka
```

**Everything uses Kafka** - no PubSub or other message brokers needed!

## 🎯 Features

- **Pure Kafka Streaming**: End-to-end Kafka for all data streaming (no PubSub needed)
- **GCP Ready**: Configured for Kafka on Google Cloud Platform
- **Simple Queue Management**: Users join, get matched, simple and clean
- **Flexible Matchmaking**: Pluggable matchmaking algorithm via callbacks
- **Real-Time Processing**: Process users joining 5+ seconds apart
- **Auto-Matching**: Background thread continuously attempts to create matches
- **Graceful Shutdown**: Proper signal handling and cleanup
- **Production Ready**: Thread-safe, error handling, logging, monitoring

## 📁 Project Structure

```
gamematchmaking/
├── config.py           # Kafka configuration for GCP
├── models.py           # User model only
├── queue_manager.py    # Simple queue management
├── producer.py         # Kafka producer (sends users)
├── consumer.py         # Kafka consumer (receives & queues users)
├── main.py            # Main orchestrator
├── requirements.txt   # Python dependencies
├── .env.example       # Environment configuration
└── README.md          # This file
```

## 🚀 Quick Start

### 1. Prerequisites

- Python 3.8+
- Kafka cluster on GCP (or local for testing)
- pip (Python package manager)

### 2. Installation

```bash
# Clone the repository
cd gamematchmaking

# Install dependencies
pip install -r requirements.txt

# Copy environment configuration
cp .env.example .env

# Edit .env with your Kafka configuration
nano .env
```

### 3. Configuration

Edit `.env` file with your Kafka settings:

```bash
# Local Kafka (for testing)
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
KAFKA_TOPIC_MATCHMAKING=matchmaking-queue
KAFKA_CONSUMER_GROUP=matchmaking-consumer-group

# GCP Kafka (production)
# KAFKA_BOOTSTRAP_SERVERS=your-gcp-kafka-broker:9092
# GCP_PROJECT_ID=your-project-id
# GCP_KAFKA_CLUSTER=your-kafka-cluster
```

### 4. Run the System

#### Start Consumer (Matchmaking Service)

```bash
python main.py consumer
```

This starts the matchmaking service that:
- Consumes user events from Kafka
- Manages the matchmaking queue
- Automatically creates matches using your algorithm
- Calls your callback when matches are found

#### Send Test Events (Producer)

In a separate terminal:

```bash
python main.py producer
```

This sends test users to the queue to verify the system works.

## 🔧 Integration Points

### 1. Matchmaking Algorithm

Implement your custom matching logic in `main.py`:

```python
def matchmaking_algorithm(user1: User, user2: User) -> bool:
    """
    Determine if two users can be matched
    
    Add your complex logic here:
    - MMR with acceptance interval
    - Region compatibility
    - Queue time considerations
    - Player preferences
    - Skill progression
    - etc.
    """
    MMR_TOLERANCE = 200
    
    # Region check
    if user1.region != user2.region:
        return False
    
    # MMR check
    mmr_diff = abs(user1.mmr - user2.mmr)
    if mmr_diff > MMR_TOLERANCE:
        return False
    
    # Add more criteria...
    
    return True
```

### 2. Match Found Handler

Handle match creation in `main.py`:

```python
def on_match_found(match: Match) -> None:
    """
    Called when a match is created
    
    Implement your game session logic:
    - Create game session
    - Notify players
    - Update database
    - Send to game outcome system
    """
    # Create game session
    create_game_session(match)
    
    # Notify players
    notify_players(match.player1, match.player2)
    
    # Update database
    save_match_to_db(match)
    
    # Send to game outcome system
    send_to_outcome_system(match)
```
treaming Data Integration (Synthetic Users)

**Your synthetic data generator streams directly to Kafka!**

See [example_data_streaming.py](example_data_streaming.py) for complete examples.

```python
from producer import MatchmakingProducer
from models import User, Region
from datetime import datetime

# Stream users continuously to Kafka
with MatchmakingProducer() as producer:
    # Generate synthetic user (from your data generator)
    user = User(
        user_id="user_123",
        mmr=1500,
        region=Region.EU,
        queue_timestamp=datetime.now().timestamp(),
        username="PlayerOne"
    )
    
    # Stream to Kafka - this feeds the entire pipeline
    producer.send_user_joined(user)
```

**Test streaming:**
```bash
# Continuous streaming (simulates real traffic)
python example_data_streaming.py continuous

# Batch mode (test with 20 users)
python example_data_streaming.py batch
producer.send_user_joined(user)
```

## 📊 Example Output

```
2026-02-09 10:30:15 - INFO - 👤 user_A (MMR=1250, EU) joined (queue: 0)
2026-02-09 10:30:16 - INFO - 👤 user_B (MMR=850, NA) joined (queue: 1)
2026-02-09 10:30:17 - INFO - 👤 user_C (MMR=1270, EU) joined (queue: 2)
2026-02-09 10:30:17 - INFO - ✅ MATCHED user_A vs user_C
2026-02-09 10:30:18 - INFO - 👤 user_D (MMR=860, NA) joined (queue: 1)
2026-02-09 10:30:18 - INFO - ✅ MATCHED user_B vs user_D
```

## 🎮 How It Works

### Queue Management

1. **Enqueue**: Users join and are added to the queue
2. **Match Attempt**: Background thread tries to match users every 2 seconds
3. **Dequeue**: Matched users are removed from queue
4. **Requeue**: Failed matches can be requeued (optional)

### Time Tolerance

Users joining 5+ seconds apart can still be matched:
- Queue persists users until matched
- Background thread continuously scans for matches
- First-come-first-served with matchmaking criteria

### Thread Safety

- All queue operations use reentrant locks
- Safe for concurrent producer/consumer operations
- Multiple consumers can run in parallel

## 🛠️ Advanced Usage

### Custom Queue Behavior

```python
from queue_manager import MatchmakingQueue

# Create queue with custom callback
queue = MatchmakingQueue(matchmaking_callback=your_algorithm)

# Queue operations
queue.enqueue(user)  # Add user to queue

# Get queue status
snapshot = queue.get_queue_snapshot()
matches = queue.get_match_history(limit=100)
```

### Multiple Consumers

Run multiple consumers for horizontal scaling:

```bash
# Terminal 1
KAFKA_CONSUMER_GROUP=group1 python main.py consumer

# Terminal 2
KAFKA_CONSUMER_GROUP=group2 python main.py consumer
```

### Monitoring

```python
# Get real-time statistics
status = consumer.get_queue_status()
print(f"Queue size: {status['queue_size']}")
print(f"Matches created: {status['matches_created']}")
print(f"Queue snapshot: {status['queue_snapshot']}")
```

## 🐛 Troubleshooting

### Kafka Connection Issues

```bash
# Test Kafka connectivity
telnet your-kafka-broker 9092

# Check Kafka topics
kafka-topics --bootstrap-server localhost:9092 --list

# Create topic if needed
kafka-topics --bootstrap-server localhost:9092 --create --topic matchmaking-queue
```

### No Matches Being Created

1. Check matchmaking algorithm logic
2. Verify MMR tolerance settings
3. Check region compatibility
4. Review logs for matching attempts

### Performance Tuning

Adjust in `config.py`:
```python
batch_size = 16384           # Kafka batch size
linger_ms = 10               # Kafka b (primary)
- `confluent-kafka`: Alternative Kafka client optimized for GCP
- `python-dotenv`: Environment configuration
- `pydantic`: Data validation

**Note:** Uses pure Kafka - no PubSub or additional message brokers required!
```python
match_interval = 2.0         # Match attempt frequency (seconds)
```

## 📦 Dependencies

- `kafka-python`: Kafka client library
- `confluent-kafka`: Alternative Kafka client (for GCP)
- `google-cloud-pubsub`: GCP Pub/Sub integration
- `python-dotenv`: Environment configuration
- `pydantic`: Data validation

## 🚀 Deployment on GCP

### 1. Setup Kafka on GCP

Options:
- **Confluent Cloud on GCP**: Managed Kafka service
- **GCP Compute Engine**: Self-hosted Kafka cluster
- **Kubernetes on GKE**: Containerized Kafka

### 2. Deploy Service

```bash
# Build Docker image
docker build -t gcr.io/YOUR_PROJECT/matchmaking:latest .

# Push to GCP
docker push gcr.io/YOUR_PROJECT/matchmaking:latest

# Deploy to Cloud Run or GKE
gcloud run deploy matchmaking --image gcr.io/YOUR_PROJECT/matchmaking:latest
```

### 3. Configure Auto-Scaling

Set horizontal pod autoscaling based on:
- Queue depth
- CPU usage
- Message lag

## 📝 Next Steps

Now that you have the Kafka middleware, you can:

1. ✅ **Synthetic Data**: Create user data generator
2. ✅ **Matchmaking Algorithm**: Implement complex matching logic
3. ✅ **Database**: Add persistence layer
4. ✅ **Game Outcome**: Build outcome determination system
5. ✅ **Monitoring**: Add Prometheus/Grafana metrics
6. ✅ **Testing**: Load testing and performance optimization

## 📄 License

This project is provided as-is for educational purposes.

## 🤝 Contributing

Feel free to extend and modify for your specific use case!

---

**Built with ❤️ for high-performance game matchmaking**
