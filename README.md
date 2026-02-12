# Game Matchmaking System with Google Pub/Sub

A real-time matchmaking system built with Google Cloud Platform, using Pub/Sub for message queuing and Cloud Run for serverless compute.

## Architecture

- **Publisher (Streamer)**: Cloud Run service that reads users from Cloud SQL and publishes to Pub/Sub
- **Subscriber (Consumer)**: Cloud Run service that consumes messages and performs matchmaking
- **Message Queue**: Google Pub/Sub (fully managed, no infrastructure needed)
- **Database**: Cloud SQL (PostgreSQL)

## Quick Start

See [GCP_SETUP.md](./GCP_SETUP.md) for complete infrastructure setup.

## Key Features

- ✅ Fully serverless - scales to zero when not in use
- ✅ No VPC configuration needed
- ✅ Automatic credential management via IAM
- ✅ Built-in message retry and dead-letter queues
- ✅ Simple monitoring via GCP Console
