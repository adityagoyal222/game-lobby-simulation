"""
Simple database initialization script
Run this once to create tables in your Cloud SQL database

Usage: python -m src.scripts.init_db
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv
from src.clients.database import connect_db, init_db, close_db

# Load environment variables
load_dotenv()


def create_database_if_not_exists():
    """Create the database if it doesn't exist"""
    db_name = os.getenv("DB_NAME", "matchmaking_db")
    db_user = os.getenv("DB_USER", "postgres")
    db_password = os.getenv("DB_PASSWORD", "")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", "5432"))

    conn = None
    cursor = None

    try:
        # Connect to PostgreSQL server (not to a specific database)
        print(f"Checking if database '{db_name}' exists...")
        conn = psycopg2.connect(
            dbname="postgres",  # Connect to default postgres database
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        # Check if database exists
        cursor.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s",
            (db_name,)
        )
        exists = cursor.fetchone()

        if not exists:
            # Create database
            print(f"Database '{db_name}' does not exist. Creating...")
            try:
                cursor.execute(f'CREATE DATABASE "{db_name}"')
                print(f"Database '{db_name}' created successfully!")
            except psycopg2.Error as create_error:
                if "permission denied" in str(create_error).lower():
                    print(f"\nWarning: Cannot create database (permission denied).")
                    print(f"Please create the database manually:")
                    print(f"  psql -U postgres -c 'CREATE DATABASE {db_name};'")
                    print(f"\nOr grant CREATEDB permission to user '{db_user}':")
                    print(f"  psql -U postgres -c 'ALTER USER {db_user} CREATEDB;'")
                    return False
                else:
                    raise
        else:
            print(f"Database '{db_name}' already exists.")

        return True

    except psycopg2.Error as e:
        print(f"PostgreSQL error: {e}")
        return False
    except Exception as e:
        print(f"Error creating database: {e}")
        return False
    finally:
        # Always close cursor and connection
        if cursor:
            cursor.close()
        if conn:
            conn.close()


if __name__ == "__main__":
    print("Initializing database...")

    # Step 1: Create database if it doesn't exist
    if not create_database_if_not_exists():
        print("Failed to create database")
        print("\nPlease check your .env file and make sure:")
        print("  - DB_HOST is set correctly")
        print("  - DB_USER has correct permissions")
        print("  - DB_PASSWORD is correct")
        exit(1)

    # Step 2: Connect to the database
    if connect_db():
        print("Connected to database")

        # Step 3: Create tables
        if init_db():
            print("Database initialized successfully!")
            print("\nYour database is ready to use.")
        else:
            print("Failed to initialize database")
    else:
        print("Failed to connect to database")
        print("\nPlease check your .env file and make sure:")
        print("  - DB_HOST is set correctly")
        print("  - DB_NAME is set correctly")
        print("  - DB_USER has correct permissions")
        print("  - DB_PASSWORD is correct")

    # Close connection
    close_db()
