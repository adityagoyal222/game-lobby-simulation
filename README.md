# GAME LOBBY SIMULATION 
###### (Name Subject To Change)

Just a simple project that tries to create a matchmaking system for a 2-fighter co-op game.


## Folder structure
```
.
├── requirements.py       # List of packages         
├── setup.py              # Makes the folders discoverable
├── SETUP.md              # Setup Guide
├── README.md             # Documentation
└── src                   # Source files
    ├── clients           # Configuration files for clients (db, kafka, etc)
    ├── matchmaking       # Code that runs on the matchmaking server
    ├── models            # Models/Tables for database
    ├── scripts           # Scripts to perform infrequent tasks
    └── simulator         # Code that runs on the streaming server
```

## Tools Used
- Cloud Provider: GCP
- Database: Cloud SQL/Postgres
- Streaming/Message Broker: Apache Kafka
- ORM: peewee