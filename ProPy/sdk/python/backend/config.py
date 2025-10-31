"""
ProTRACE Backend Configuration
Production-ready configuration management for all environments
"""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseSettings, Field


class Environment(str, Enum):
    """Deployment environment"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEVNET = "devnet"


class Settings(BaseSettings):
    """Application settings with environment variable support"""
    
    # Application
    APP_NAME: str = "ProTRACE API"
    APP_VERSION: str = "1.0.0"
    ENVIRONMENT: Environment = Environment.DEVELOPMENT
    DEBUG: bool = False
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False
    
    # API
    API_PREFIX: str = "/api/v1"
    CORS_ORIGINS: list = ["*"]
    RATE_LIMIT: int = 100  # requests per minute
    
    # Database (for production)
    DATABASE_URL: Optional[str] = None
    DB_POOL_SIZE: int = 10
    
    # Redis (for caching/sessions)
    REDIS_URL: Optional[str] = None
    CACHE_TTL: int = 3600  # seconds
    
    # Storage
    DATA_DIR: str = "./data"
    REGISTRY_DIR: str = "./registry"
    MERKLE_DIR: str = "./merkle_nodes"
    
    # Image Processing
    DNA_HASH_SIZE: int = 64  # hex characters
    SIMILARITY_THRESHOLD: float = 0.90
    MAX_IMAGE_SIZE: int = 10 * 1024 * 1024  # 10MB
    
    # IPFS
    IPFS_API_URL: str = "http://localhost:5001"
    IPFS_GATEWAY_URL: str = "http://localhost:8080"
    IPFS_ENABLED: bool = False
    
    # Blockchain - Ethereum
    ETH_RPC_URL: Optional[str] = None
    ETH_CHAIN_ID: int = 1  # 1=mainnet, 5=goerli, 11155111=sepolia
    ETH_CONTRACT_ADDRESS: Optional[str] = None
    ETH_PRIVATE_KEY: Optional[str] = None
    
    # Blockchain - Solana
    SOLANA_RPC_URL: str = "https://api.devnet.solana.com"
    SOLANA_CLUSTER: str = "devnet"  # devnet, testnet, mainnet-beta
    SOLANA_PROGRAM_ID: Optional[str] = None
    SOLANA_KEYPAIR_PATH: Optional[str] = None
    
    # Blockchain - Tezos
    TEZOS_RPC_URL: str = "https://ghostnet.ecadinfra.com"
    TEZOS_NETWORK: str = "ghostnet"  # ghostnet, mainnet
    TEZOS_CONTRACT_ADDRESS: Optional[str] = None
    
    # Vector Database
    VECTOR_DB_ENABLED: bool = False
    VECTOR_DB_URL: Optional[str] = None
    VECTOR_DIM: int = 256  # DNA hash embedding dimension
    
    # Security
    SECRET_KEY: str = "change-this-in-production"
    API_KEY_ENABLED: bool = False
    JWT_SECRET: Optional[str] = None
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"  # json or text
    LOG_FILE: Optional[str] = None
    
    # Monitoring
    METRICS_ENABLED: bool = False
    SENTRY_DSN: Optional[str] = None
    
    # Testing
    TEST_MODE: bool = False
    TEST_DATA_DIR: str = "./test_data"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton settings instance
settings = Settings()


# Environment-specific configurations
def get_devnet_config() -> dict:
    """Devnet-specific configuration"""
    return {
        "ENVIRONMENT": Environment.DEVNET,
        "DEBUG": True,
        "SOLANA_RPC_URL": "https://api.devnet.solana.com",
        "SOLANA_CLUSTER": "devnet",
        "ETH_CHAIN_ID": 11155111,  # Sepolia
        "ETH_RPC_URL": "https://sepolia.infura.io/v3/YOUR_KEY",
        "TEZOS_NETWORK": "ghostnet",
        "IPFS_ENABLED": False,
        "VECTOR_DB_ENABLED": False,
        "RATE_LIMIT": 1000,
        "LOG_LEVEL": "DEBUG",
    }


def get_production_config() -> dict:
    """Production-specific configuration"""
    return {
        "ENVIRONMENT": Environment.PRODUCTION,
        "DEBUG": False,
        "RELOAD": False,
        "WORKERS": 8,
        "DATABASE_URL": "postgresql://user:pass@localhost/protrace",
        "REDIS_URL": "redis://localhost:6379",
        "IPFS_ENABLED": True,
        "VECTOR_DB_ENABLED": True,
        "API_KEY_ENABLED": True,
        "METRICS_ENABLED": True,
        "LOG_LEVEL": "INFO",
        "LOG_FORMAT": "json",
        "CORS_ORIGINS": ["https://protrace.io"],
    }


def get_testing_config() -> dict:
    """Testing-specific configuration"""
    return {
        "ENVIRONMENT": Environment.TESTING,
        "DEBUG": True,
        "TEST_MODE": True,
        "DATABASE_URL": "sqlite:///test.db",
        "IPFS_ENABLED": False,
        "VECTOR_DB_ENABLED": False,
        "SOLANA_RPC_URL": "http://localhost:8899",  # Local validator
        "LOG_LEVEL": "DEBUG",
    }


def configure_environment(env: Environment):
    """Apply environment-specific configuration"""
    global settings
    
    config_map = {
        Environment.DEVNET: get_devnet_config(),
        Environment.PRODUCTION: get_production_config(),
        Environment.TESTING: get_testing_config(),
    }
    
    if env in config_map:
        for key, value in config_map[env].items():
            setattr(settings, key, value)
    
    return settings
