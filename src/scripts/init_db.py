#!/usr/bin/env python3
print("=" * 60)
print("DATABASE INITIALIZATION")
print("=" * 60)
print("Testing Cloud SQL connection...")
from src.clients.database import connect_db, close_db, init_db
from src.models.user_model import UserModel  # Import models so they're registered with Base

if connect_db():
    print("SUCCESS: Database connection established!")
    print("\nCreating database tables...")
    init_db()
    print("SUCCESS: Database tables created successfully!")
    print("=" * 60)
    close_db()
    exit(0)
else:
    print("FAILED: Could not connect to database")
    print("=" * 60)
    exit(1)
