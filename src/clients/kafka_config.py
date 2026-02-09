"""
Kafka Configuration Module
Handles Kafka connection settings for GCP
Pure Kafka streaming - no PubSub needed!
"""
import os
from dataclasses import dataclass
from typing import Optional
from dotenv import load_dotenv

load_dotenv()


@dataclass
class KafkaConfig:
    """Kafka configuration for producer and consumer"""
    
    bootstrap_servers: str
    topic_matchmaking: str
    consumer_group: str
    
    # GCP specific settings
    gcp_project_id: Optional[str] = None
    gcp_kafka_cluster: Optional[str] = None
    
    # Performance tuning
    batch_size: int = 16384
    linger_ms: int = 10
    compression_type: str = "snappy"
    
    # Consumer settings
    auto_offset_reset: str = "earliest"
    enable_auto_commit: bool = True
    max_poll_records: int = 100
    session_timeout_ms: int = 10000
    
    @classmethod
    def from_env(cls) -> "KafkaConfig":
        """Load configuration from environment variables"""
        return cls(
            bootstrap_servers=os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"),
            topic_matchmaking=os.getenv("KAFKA_TOPIC_MATCHMAKING", "matchmaking-queue"),
            consumer_group=os.getenv("KAFKA_CONSUMER_GROUP", "matchmaking-consumer-group"),
            gcp_project_id=os.getenv("GCP_PROJECT_ID"),
            gcp_kafka_cluster=os.getenv("GCP_KAFKA_CLUSTER"),
        )
    
    def get_producer_config(self) -> dict:
        """Get producer configuration dictionary"""
        config = {
            "bootstrap_servers": self.bootstrap_servers.split(","),
            "batch_size": self.batch_size,
            "linger_ms": self.linger_ms,
            "compression_type": self.compression_type,
            "acks": "all",  # Wait for all replicas to acknowledge
            "retries": 3,
        }
        
        # Add GCP authentication if configured
        if self.gcp_project_id and self.gcp_kafka_cluster:
            config.update(self._get_gcp_auth_config())
        
        return config
    
    def get_consumer_config(self) -> dict:
        """Get consumer configuration dictionary"""
        config = {
            "bootstrap_servers": self.bootstrap_servers.split(","),
            "group_id": self.consumer_group,
            "auto_offset_reset": self.auto_offset_reset,
            "enable_auto_commit": self.enable_auto_commit,
            "max_poll_records": self.max_poll_records,
            "session_timeout_ms": self.session_timeout_ms,
        }
        
        # Add GCP authentication if configured
        if self.gcp_project_id and self.gcp_kafka_cluster:
            config.update(self._get_gcp_auth_config())
        
        return config
    
    def _get_gcp_auth_config(self) -> dict:
        """Get GCP-specific authentication configuration"""
        # This would be configured based on GCP Kafka setup
        # For managed Kafka on GCP (like Confluent Cloud on GCP)
        return {
            "security_protocol": "SASL_SSL",
            "sasl_mechanism": "PLAIN",
            # Add GCP-specific credentials here
        }
