"""
Database connection and session management using SQLAlchemy
"""
import os
from dotenv import load_dotenv
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base
from sqlalchemy.pool import NullPool
from google.cloud.sql.connector import Connector, IPTypes

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# SQLAlchemy components
Base = declarative_base()
engine = None
Session = None
connector = None

def getconn():
    """Create database connection for Cloud SQL using pg8000"""
    global connector
    if connector is None:
        connector = Connector(ip_type=IPTypes.PUBLIC)

    instance_name = os.getenv("DB_CONNECTION_NAME") or os.getenv("INSTANCE_CONNECTION_NAME")
    conn = connector.connect(
        instance_name,
        "pg8000",
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        db=os.getenv("DB_NAME")
    )
    return conn

def connect_db():
    """Initialize SQLAlchemy engine and session factory"""
    global engine, Session
    try:
        # Check if DB_HOST is set (private IP) or use Cloud SQL Connector
        db_host = os.getenv("DB_HOST")
        
        if db_host:
            # Direct connection via private IP (for VPC)
            print(f"Connecting to Cloud SQL via private IP: {db_host}")
            connection_string = (
                f"postgresql+pg8000://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
                f"@{db_host}:5432/{os.getenv('DB_NAME')}"
            )
            engine = create_engine(
                connection_string,
                poolclass=NullPool,
                echo=False
            )
        else:
            # Cloud SQL Connector (for public IP)
            print("Connecting to Cloud SQL via Connector...")
            engine = create_engine(
                "postgresql+pg8000://",
                creator=getconn,
                poolclass=NullPool,
                echo=False
            )
        
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        
        # Create session factory
        Session = scoped_session(sessionmaker(bind=engine))
        
        print("CLOUD SQL CONNECTED SUCCESSFULLY!")
        logger.info("Cloud SQL ready")
        return True
    except Exception as e:
        print(f"CONNECTION FAILED: {e}")
        logger.error(f"Database connection error: {e}")
        return False

def get_session():
    """Get a database session"""
    if Session is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    return Session()

def close_db():
    """Close database connections"""
    global engine, Session, connector
    if Session:
        Session.remove()
    if engine:
        engine.dispose()
    if connector:
        connector.close()

def init_db():
    """Create all tables defined in the models"""
    if engine is None:
        raise RuntimeError("Database not connected. Call connect_db() first.")
    
    print("Creating database tables...")
    Base.metadata.create_all(engine)
    print("Tables created successfully")
    return True
