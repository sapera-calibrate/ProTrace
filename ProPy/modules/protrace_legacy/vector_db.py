"""
ProTrace Vector Database Interface
==================================

PostgreSQL + pgvector integration for fast DNA similarity search.
Uses HNSW indexing for O(log n) ANN queries.
"""

from typing import List, Dict, Optional, Tuple
import json
import os


class VectorDBClient:
    """
    Vector database client for DNA similarity search.
    
    Supports:
    - PostgreSQL with pgvector extension
    - HNSW indexing for ANN queries
    - Hamming distance operations
    """
    
    def __init__(self, connection_string: str = None):
        """
        Initialize vector DB client.
        
        Args:
            connection_string: PostgreSQL connection string
                             Format: postgresql://user:pass@host:port/dbname
        """
        self.connection_string = connection_string or os.getenv(
            'POSTGRES_URL',
            'postgresql://protrace:protrace@localhost:5432/protrace'
        )
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """Establish database connection"""
        try:
            import psycopg2
            self.conn = psycopg2.connect(self.connection_string)
            self.cursor = self.conn.cursor()
            return True
        except ImportError:
            print("⚠️  psycopg2 not installed. Install with: pip install psycopg2-binary")
            return False
        except Exception as e:
            print(f"❌ Database connection failed: {e}")
            return False
    
    def close(self):
        """Close database connection"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def initialize_schema(self):
        """
        Create database schema with pgvector extension.
        
        Table: dna_registry
        - id (UUID): Pointer
        - dna_vector (BIT(128)): 128-bit DNA
        - platform_id (VARCHAR): Platform identifier
        - token_id (NUMERIC): Token ID
        - contract_address (VARCHAR): Smart contract address
        - blockchain (VARCHAR): Blockchain name
        - timestamp (TIMESTAMPTZ): Registration time
        - metadata (JSONB): Additional metadata
        - merkle_leaf_hash (BYTEA): Merkle leaf hash
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")
        
        schema_sql = """
        -- Enable pgvector extension
        CREATE EXTENSION IF NOT EXISTS pgvector;
        
        -- Create dna_registry table
        CREATE TABLE IF NOT EXISTS dna_registry (
            id UUID PRIMARY KEY,
            dna_vector BIT(128) NOT NULL,
            platform_id VARCHAR(50) NOT NULL,
            token_id NUMERIC NOT NULL,
            contract_address VARCHAR(66),
            blockchain VARCHAR(20) NOT NULL,
            timestamp TIMESTAMPTZ DEFAULT NOW(),
            metadata JSONB,
            merkle_leaf_hash BYTEA,
            CONSTRAINT unique_platform_token UNIQUE (platform_id, token_id)
        );
        
        -- Create HNSW index for fast Hamming distance queries
        CREATE INDEX IF NOT EXISTS idx_dna_hnsw 
        ON dna_registry USING hnsw ((dna_vector::bit(128))) 
        WITH (m = 16, ef_construction = 64);
        
        -- Create indexes for common queries
        CREATE INDEX IF NOT EXISTS idx_platform ON dna_registry(platform_id);
        CREATE INDEX IF NOT EXISTS idx_blockchain ON dna_registry(blockchain);
        CREATE INDEX IF NOT EXISTS idx_timestamp ON dna_registry(timestamp DESC);
        """
        
        try:
            self.cursor.execute(schema_sql)
            self.conn.commit()
            print("✅ Database schema initialized")
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Schema initialization failed: {e}")
            return False
    
    def insert_dna(self, dna_hex: str, pointer: str, platform_id: str, 
                   token_id: int, contract_address: str = None, 
                   blockchain: str = "ethereum", metadata: Dict = None) -> bool:
        """
        Insert DNA record into database.
        
        Args:
            dna_hex: 128-bit DNA as 32-char hex string
            pointer: Unique identifier (UUID)
            platform_id: Platform identifier
            token_id: Token ID
            contract_address: Smart contract address
            blockchain: Blockchain name
            metadata: Additional metadata dict
        
        Returns:
            True if successful
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")
        
        # Convert hex to binary string for BIT(128)
        dna_int = int(dna_hex, 16)
        dna_binary = bin(dna_int)[2:].zfill(128)
        
        insert_sql = """
        INSERT INTO dna_registry 
        (id, dna_vector, platform_id, token_id, contract_address, blockchain, metadata)
        VALUES (%s, %s::bit(128), %s, %s, %s, %s, %s)
        ON CONFLICT (platform_id, token_id) DO NOTHING
        """
        
        try:
            self.cursor.execute(insert_sql, (
                pointer,
                dna_binary,
                platform_id,
                token_id,
                contract_address,
                blockchain,
                json.dumps(metadata) if metadata else None
            ))
            self.conn.commit()
            return True
        except Exception as e:
            self.conn.rollback()
            print(f"❌ Insert failed: {e}")
            return False
    
    def query_similar(self, dna_hex: str, threshold: int = 20, limit: int = 5) -> List[Dict]:
        """
        Query for similar DNA vectors using ANN search.
        
        Args:
            dna_hex: Query DNA as 32-char hex string
            threshold: Maximum Hamming distance for ANN filter (default 20)
            limit: Maximum results to return
        
        Returns:
            List of similar DNA records with Hamming distances
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")
        
        # Convert hex to binary
        dna_int = int(dna_hex, 16)
        dna_binary = bin(dna_int)[2:].zfill(128)
        
        query_sql = """
        SELECT 
            id AS pointer,
            dna_vector,
            BIT_COUNT(dna_vector # %s::bit(128)) AS hamming_distance,
            platform_id,
            token_id,
            contract_address,
            blockchain,
            timestamp,
            metadata
        FROM dna_registry
        WHERE dna_vector <-> %s::bit(128) < %s
        ORDER BY hamming_distance ASC
        LIMIT %s
        """
        
        try:
            self.cursor.execute(query_sql, (dna_binary, dna_binary, threshold, limit))
            results = []
            
            for row in self.cursor.fetchall():
                # Convert BIT(128) back to hex
                dna_bits = row[1]
                dna_hex_result = hex(int(dna_bits, 2))[2:].zfill(32)
                
                results.append({
                    'pointer': row[0],
                    'dna_hex': dna_hex_result,
                    'hamming_distance': row[2],
                    'similarity_percent': round((1 - row[2] / 128.0) * 100, 2),
                    'platform_id': row[3],
                    'token_id': int(row[4]),
                    'contract_address': row[5],
                    'blockchain': row[6],
                    'timestamp': row[7].isoformat() if row[7] else None,
                    'metadata': row[8] if row[8] else {}
                })
            
            return results
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return []
    
    def check_uniqueness(self, dna_hex: str, threshold: int = 13) -> Tuple[bool, List[Dict]]:
        """
        Check if DNA is unique (no duplicates found).
        
        Per architecture: ≤13 bits = ≥90% match = duplicate
        
        Args:
            dna_hex: DNA to check
            threshold: Hamming distance threshold (default 13)
        
        Returns:
            Tuple of (is_unique: bool, candidates: List[Dict])
        """
        # Query with slightly higher threshold for ANN
        candidates = self.query_similar(dna_hex, threshold=threshold + 7, limit=10)
        
        # Filter to exact threshold
        duplicates = [c for c in candidates if c['hamming_distance'] <= threshold]
        
        return (len(duplicates) == 0, duplicates)
    
    def get_by_pointer(self, pointer: str) -> Optional[Dict]:
        """
        Get DNA record by pointer ID.
        
        Args:
            pointer: UUID pointer
        
        Returns:
            DNA record dict or None
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")
        
        query_sql = """
        SELECT dna_vector, platform_id, token_id, contract_address, 
               blockchain, timestamp, metadata
        FROM dna_registry
        WHERE id = %s
        """
        
        try:
            self.cursor.execute(query_sql, (pointer,))
            row = self.cursor.fetchone()
            
            if not row:
                return None
            
            dna_bits = row[0]
            dna_hex = hex(int(dna_bits, 2))[2:].zfill(32)
            
            return {
                'pointer': pointer,
                'dna_hex': dna_hex,
                'platform_id': row[1],
                'token_id': int(row[2]),
                'contract_address': row[3],
                'blockchain': row[4],
                'timestamp': row[5].isoformat() if row[5] else None,
                'metadata': row[6] if row[6] else {}
            }
        except Exception as e:
            print(f"❌ Query failed: {e}")
            return None
    
    def get_stats(self) -> Dict:
        """
        Get database statistics.
        
        Returns:
            Dict with total records, platforms, etc.
        """
        if not self.conn:
            raise RuntimeError("Not connected to database")
        
        stats_sql = """
        SELECT 
            COUNT(*) as total_records,
            COUNT(DISTINCT platform_id) as total_platforms,
            COUNT(DISTINCT blockchain) as total_blockchains,
            MIN(timestamp) as earliest_registration,
            MAX(timestamp) as latest_registration
        FROM dna_registry
        """
        
        try:
            self.cursor.execute(stats_sql)
            row = self.cursor.fetchone()
            
            return {
                'total_records': row[0],
                'total_platforms': row[1],
                'total_blockchains': row[2],
                'earliest_registration': row[3].isoformat() if row[3] else None,
                'latest_registration': row[4].isoformat() if row[4] else None
            }
        except Exception as e:
            print(f"❌ Stats query failed: {e}")
            return {}


# Fallback in-memory implementation for testing without PostgreSQL
class InMemoryVectorDB:
    """
    In-memory vector database for testing and development.
    Not suitable for production - use PostgreSQL + pgvector.
    """
    
    def __init__(self):
        self.records = []
    
    def connect(self):
        return True
    
    def close(self):
        pass
    
    def initialize_schema(self):
        return True
    
    def insert_dna(self, dna_hex: str, pointer: str, platform_id: str,
                   token_id: int, contract_address: str = None,
                   blockchain: str = "ethereum", metadata: Dict = None) -> bool:
        self.records.append({
            'pointer': pointer,
            'dna_hex': dna_hex,
            'platform_id': platform_id,
            'token_id': token_id,
            'contract_address': contract_address,
            'blockchain': blockchain,
            'metadata': metadata or {}
        })
        return True
    
    def query_similar(self, dna_hex: str, threshold: int = 20, limit: int = 5) -> List[Dict]:
        from .image_dna import hamming_distance
        
        results = []
        for record in self.records:
            distance = hamming_distance(dna_hex, record['dna_hex'])
            if distance < threshold:
                results.append({
                    **record,
                    'hamming_distance': distance,
                    'similarity_percent': round((1 - distance / 128.0) * 100, 2)
                })
        
        results.sort(key=lambda x: x['hamming_distance'])
        return results[:limit]
    
    def check_uniqueness(self, dna_hex: str, threshold: int = 13) -> Tuple[bool, List[Dict]]:
        candidates = self.query_similar(dna_hex, threshold=threshold + 7, limit=10)
        duplicates = [c for c in candidates if c['hamming_distance'] <= threshold]
        return (len(duplicates) == 0, duplicates)
    
    def get_by_pointer(self, pointer: str) -> Optional[Dict]:
        for record in self.records:
            if record['pointer'] == pointer:
                return record
        return None
    
    def get_stats(self) -> Dict:
        platforms = set(r['platform_id'] for r in self.records)
        blockchains = set(r['blockchain'] for r in self.records)
        
        return {
            'total_records': len(self.records),
            'total_platforms': len(platforms),
            'total_blockchains': len(blockchains)
        }


# Factory function
def create_vector_db(use_postgres: bool = True, connection_string: str = None):
    """
    Create vector database client.
    
    Args:
        use_postgres: Use PostgreSQL (True) or in-memory (False)
        connection_string: PostgreSQL connection string
    
    Returns:
        VectorDBClient or InMemoryVectorDB instance
    """
    if use_postgres:
        return VectorDBClient(connection_string)
    else:
        print("⚠️  Using in-memory vector DB (not suitable for production)")
        return InMemoryVectorDB()
