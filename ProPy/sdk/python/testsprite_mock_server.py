#!/usr/bin/env python3
"""
TestSprite Mock API Server
===========================

Localhost server that mimics API behavior for TestSprite testing.
Includes all endpoints configured for TestSprite with realistic mock responses.
"""

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import hashlib
import time
import json
import base64
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TestSprite Mock API Server",
    description="Mock API server for TestSprite automated testing",
    version="1.0.0"
)

# Add CORS middleware for TestSprite browser-based tests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    response = await call_next(request)
    duration = (time.time() - start_time) * 1000
    logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.2f}ms)")
    return response

# ============================================================================
# State Management
# ============================================================================

# In-memory storage for session data
merkle_sessions = {}
registered_images = {}
request_count = 0

# ============================================================================
# Request/Response Models
# ============================================================================

class ComputeDNARequest(BaseModel):
    image_identifier: str

class RegisterImageRequest(BaseModel):
    image_identifier: str
    image_id: str
    platform_id: str
    similarity_threshold: Optional[float] = 0.90

class MerkleTreeRequest(BaseModel):
    leaf_count: int

class EIP712SignRequest(BaseModel):
    test_scenario: Optional[str] = "valid_signature"

class EditionRegisterRequest(BaseModel):
    chain: str
    edition_no: int

# ============================================================================
# Helper Functions
# ============================================================================

def generate_mock_dna(identifier: str) -> Dict[str, str]:
    """Generate deterministic mock DNA hash"""
    base_hash = hashlib.sha256(identifier.encode()).hexdigest()
    dhash = base_hash[:16]
    grid_hash = base_hash[16:64]
    dna_hex = dhash + grid_hash
    return {
        "dna_hex": dna_hex,
        "dhash": dhash,
        "grid_hash": grid_hash
    }

def increment_request_count():
    """Track API usage"""
    global request_count
    request_count += 1
    return request_count

# ============================================================================
# ROOT & HEALTH ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Root endpoint - API information"""
    return {
        "name": "TestSprite Mock API Server",
        "version": "1.0.0",
        "description": "Mock API for TestSprite automated testing",
        "status": "operational",
        "endpoints": {
            "health": "/health",
            "compute_dna": "/test/compute_dna",
            "register_image": "/test/register_image",
            "build_merkle": "/test/build_merkle",
            "merkle_proof": "/test/merkle_proof/{session_id}/{leaf_index}",
            "eip712_sign": "/test/eip712_sign",
            "edition_register": "/test/edition_register",
            "vector_search": "/test/vector_search",
            "ipfs_upload": "/test/ipfs_upload",
            "relayer_monitor": "/test/relayer_monitor",
            "solana_register": "/test/solana_register"
        },
        "request_count": request_count,
        "documentation": "/docs"
    }

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": "operational",
        "request_count": request_count,
        "registered_images": len(registered_images),
        "merkle_sessions": len(merkle_sessions)
    }

# ============================================================================
# API ENDPOINT 1: COMPUTE DNA FINGERPRINT
# ============================================================================

@app.get("/test/compute_dna")
async def compute_dna_get():
    """Compute DNA - GET method for browser/TestSprite navigation"""
    increment_request_count()
    dna_data = generate_mock_dna("demo_image_001")
    return {
        "success": True,
        "dna_hex": dna_data["dna_hex"],
        "dhash": dna_data["dhash"],
        "grid_hash": dna_data["grid_hash"],
        "test_mode": True,
        "image_identifier": "demo_image_001",
        "timestamp": int(time.time()),
        "note": "GET demo. Use POST with body for custom image_identifier."
    }

@app.post("/test/compute_dna")
async def compute_dna_post(request: ComputeDNARequest):
    """Compute DNA - POST method with custom parameters"""
    increment_request_count()
    dna_data = generate_mock_dna(request.image_identifier)
    return {
        "success": True,
        "dna_hex": dna_data["dna_hex"],
        "dhash": dna_data["dhash"],
        "grid_hash": dna_data["grid_hash"],
        "test_mode": True,
        "image_identifier": request.image_identifier,
        "timestamp": int(time.time())
    }

# ============================================================================
# API ENDPOINT 2: REGISTER IMAGE
# ============================================================================

@app.get("/test/register_image")
async def register_image_get():
    """Register Image - GET method for browser/TestSprite navigation"""
    increment_request_count()
    image_id = f"demo_img_{int(time.time())}"
    dna_data = generate_mock_dna(f"demo_unique_{image_id}")
    root_hash = hashlib.sha256(f"{dna_data['dna_hex']}{image_id}".encode()).hexdigest()
    
    return {
        "success": True,
        "plagiarized": False,
        "root_hash": root_hash,
        "match": None,
        "dna_hex": dna_data["dna_hex"],
        "image_id": image_id,
        "platform_id": "demo_platform",
        "test_mode": True,
        "timestamp": int(time.time()),
        "note": "GET demo. Use POST with body for custom registration."
    }

@app.post("/test/register_image")
async def register_image_post(request: RegisterImageRequest):
    """Register Image - POST method with duplicate detection"""
    increment_request_count()
    
    # Check if identifier ends with "_duplicate" to simulate duplicate detection
    is_duplicate = request.image_identifier.endswith("_duplicate")
    
    dna_data = generate_mock_dna(request.image_identifier)
    
    if is_duplicate:
        # Simulate duplicate found
        original_id = request.image_identifier.replace("_duplicate", "")
        return {
            "success": False,
            "plagiarized": True,
            "root_hash": None,
            "match": {
                "image_id": original_id,
                "similarity": 0.95,
                "platform_id": request.platform_id,
                "registered_at": int(time.time()) - 3600,
                "dna_hex": generate_mock_dna(original_id)["dna_hex"]
            },
            "dna_hex": dna_data["dna_hex"],
            "test_mode": True,
            "timestamp": int(time.time())
        }
    else:
        # Successful registration
        root_hash = hashlib.sha256(f"{dna_data['dna_hex']}{request.image_id}".encode()).hexdigest()
        
        # Store in registry
        registered_images[request.image_id] = {
            "image_identifier": request.image_identifier,
            "dna_hex": dna_data["dna_hex"],
            "platform_id": request.platform_id,
            "registered_at": int(time.time())
        }
        
        return {
            "success": True,
            "plagiarized": False,
            "root_hash": root_hash,
            "match": None,
            "dna_hex": dna_data["dna_hex"],
            "image_id": request.image_id,
            "platform_id": request.platform_id,
            "test_mode": True,
            "timestamp": int(time.time())
        }

# ============================================================================
# API ENDPOINT 3: BUILD MERKLE TREE
# ============================================================================

@app.get("/test/build_merkle")
async def build_merkle_get():
    """Build Merkle Tree - GET method"""
    increment_request_count()
    leaf_count = 5
    leaves = [f"mock_dna_hash_{i}" for i in range(leaf_count)]
    combined = "".join(leaves)
    root_hash = hashlib.sha256(combined.encode()).hexdigest()
    session_id = hashlib.sha256(f"{root_hash}{time.time()}".encode()).hexdigest()[:16]
    
    # Store session
    merkle_sessions[session_id] = {
        "root_hash": root_hash,
        "leaves": leaves,
        "created_at": int(time.time())
    }
    
    return {
        "success": True,
        "root_hash": root_hash,
        "leaf_count": leaf_count,
        "session_id": session_id,
        "test_mode": True,
        "timestamp": int(time.time()),
        "note": "GET demo. Use POST with body for custom leaf_count."
    }

@app.post("/test/build_merkle")
async def build_merkle_post(request: MerkleTreeRequest):
    """Build Merkle Tree - POST method"""
    increment_request_count()
    leaves = [f"mock_dna_hash_{i}" for i in range(request.leaf_count)]
    combined = "".join(leaves)
    root_hash = hashlib.sha256(combined.encode()).hexdigest()
    session_id = hashlib.sha256(f"{root_hash}{time.time()}".encode()).hexdigest()[:16]
    
    # Store session
    merkle_sessions[session_id] = {
        "root_hash": root_hash,
        "leaves": leaves,
        "created_at": int(time.time())
    }
    
    return {
        "success": True,
        "root_hash": root_hash,
        "leaf_count": request.leaf_count,
        "session_id": session_id,
        "test_mode": True,
        "timestamp": int(time.time()),
        "leaves_preview": leaves[:3] + ["..."] if request.leaf_count > 3 else leaves
    }

# ============================================================================
# API ENDPOINT 4: GET MERKLE PROOF
# ============================================================================

@app.get("/test/merkle_proof/{session_id}/{leaf_index}")
async def get_merkle_proof(session_id: str, leaf_index: int):
    """Get Merkle Proof for a specific leaf"""
    increment_request_count()
    
    # Check if session exists
    if session_id in merkle_sessions:
        session_data = merkle_sessions[session_id]
        root_hash = session_data["root_hash"]
    else:
        # Generate proof even for unknown sessions (for testing)
        root_hash = hashlib.sha256(f"{session_id}_root".encode()).hexdigest()
    
    # Generate proof hashes
    proof = [
        hashlib.sha256(f"{session_id}_sibling_{i}".encode()).hexdigest()
        for i in range(3)  # 3 levels in the tree
    ]
    
    return {
        "success": True,
        "leaf_index": leaf_index,
        "proof": proof,
        "root_hash": root_hash,
        "session_id": session_id,
        "test_mode": True,
        "timestamp": int(time.time())
    }

# ============================================================================
# API ENDPOINT 5: EIP-712 SIGNATURE
# ============================================================================

@app.get("/test/eip712_sign")
async def eip712_sign_get():
    """EIP-712 Sign - GET method"""
    increment_request_count()
    
    message_data = {
        "creator_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "asset_hash": "0x" + hashlib.sha256(b"demo_asset").hexdigest(),
        "rights": "commercial",
        "token_type": "ERC721",
        "timestamp": int(time.time())
    }
    
    signature_input = json.dumps(message_data, sort_keys=True)
    signature = "0x" + hashlib.sha256(signature_input.encode()).hexdigest() + \
                hashlib.sha256((signature_input + "v").encode()).hexdigest()[:64]
    digest = "0x" + hashlib.sha256(signature_input.encode()).hexdigest()
    
    return {
        "success": True,
        "signature": signature,
        "digest": digest,
        "message": message_data,
        "test_mode": True,
        "timestamp": int(time.time()),
        "note": "GET demo. Use POST with body for custom scenarios."
    }

@app.post("/test/eip712_sign")
async def eip712_sign_post(request: EIP712SignRequest):
    """EIP-712 Sign - POST method"""
    increment_request_count()
    
    message_data = {
        "creator_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "asset_hash": "0x" + hashlib.sha256(b"test_asset").hexdigest(),
        "rights": "commercial",
        "token_type": "ERC721",
        "scenario": request.test_scenario,
        "timestamp": int(time.time())
    }
    
    signature_input = json.dumps(message_data, sort_keys=True)
    signature = "0x" + hashlib.sha256(signature_input.encode()).hexdigest() + \
                hashlib.sha256((signature_input + "v").encode()).hexdigest()[:64]
    digest = "0x" + hashlib.sha256(signature_input.encode()).hexdigest()
    
    return {
        "success": True,
        "signature": signature,
        "digest": digest,
        "message": message_data,
        "test_mode": True,
        "timestamp": int(time.time())
    }

# ============================================================================
# API ENDPOINT 6: REGISTER EDITION
# ============================================================================

@app.get("/test/edition_register")
async def edition_register_get():
    """Register Edition - GET method"""
    increment_request_count()
    
    chain = "ethereum"
    edition_no = 1
    universal_key = hashlib.sha256(f"{chain}_{edition_no}".encode()).hexdigest()[:32]
    
    return {
        "success": True,
        "chain": chain,
        "edition_no": edition_no,
        "max_editions": 100,
        "universal_key": universal_key,
        "contract": "0x" + hashlib.sha256(chain.encode()).hexdigest()[:40],
        "token_id": str(edition_no),
        "test_mode": True,
        "timestamp": int(time.time()),
        "note": "GET demo. Use POST with body for custom chain/edition."
    }

@app.post("/test/edition_register")
async def edition_register_post(request: EditionRegisterRequest):
    """Register Edition - POST method"""
    increment_request_count()
    
    universal_key = hashlib.sha256(f"{request.chain}_{request.edition_no}".encode()).hexdigest()[:32]
    
    return {
        "success": True,
        "chain": request.chain,
        "edition_no": request.edition_no,
        "max_editions": 100,
        "universal_key": universal_key,
        "contract": "0x" + hashlib.sha256(request.chain.encode()).hexdigest()[:40],
        "token_id": str(request.edition_no),
        "test_mode": True,
        "timestamp": int(time.time())
    }

# ============================================================================
# API ENDPOINT 7: VECTOR SEARCH
# ============================================================================

@app.get("/test/vector_search")
@app.post("/test/vector_search")
async def vector_search():
    """Vector Similarity Search"""
    increment_request_count()
    
    results = [
        {
            "dna_hash": hashlib.sha256(f"similar_dna_{i}".encode()).hexdigest()[:64],
            "similarity": 0.95 - (i * 0.02),
            "metadata": {
                "image_id": f"img_{i}",
                "platform_id": "test_platform",
                "timestamp": int(time.time()) - (i * 3600)
            }
        }
        for i in range(3)
    ]
    
    return {
        "success": True,
        "results": results,
        "count": len(results),
        "threshold": 0.90,
        "test_mode": True,
        "timestamp": int(time.time())
    }

# ============================================================================
# API ENDPOINT 8: IPFS UPLOAD
# ============================================================================

@app.get("/test/ipfs_upload")
@app.post("/test/ipfs_upload")
async def ipfs_upload():
    """IPFS Manifest Upload"""
    increment_request_count()
    
    manifest = {
        "dna_hash": hashlib.sha256(b"test_manifest").hexdigest(),
        "timestamp": int(time.time()),
        "version": "1.0",
        "metadata": {
            "creator": "test_creator",
            "platform": "test_platform"
        }
    }
    
    cid_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    cid = "Qm" + base64.b32encode(bytes.fromhex(cid_hash[:40])).decode()[:44]
    
    return {
        "success": True,
        "cid": cid,
        "manifest": manifest,
        "size": len(json.dumps(manifest)),
        "test_mode": True,
        "timestamp": int(time.time())
    }

# ============================================================================
# API ENDPOINT 9: RELAYER MONITOR
# ============================================================================

@app.get("/test/relayer_monitor")
@app.post("/test/relayer_monitor")
async def relayer_monitor():
    """Blockchain Event Relayer"""
    increment_request_count()
    
    monitor_id = hashlib.sha256(f"monitor_{time.time()}".encode()).hexdigest()[:16]
    
    return {
        "success": True,
        "monitor_id": monitor_id,
        "chain": "ethereum",
        "contract_address": "0x" + hashlib.sha256(b"test_contract").hexdigest()[:40],
        "event_types": ["Transfer", "Approval", "Mint"],
        "status": "monitoring",
        "test_mode": True,
        "timestamp": int(time.time())
    }

# ============================================================================
# API ENDPOINT 10: SOLANA REGISTER DNA
# ============================================================================

@app.get("/test/solana_register")
@app.post("/test/solana_register")
async def solana_register():
    """Solana DNA Registration"""
    increment_request_count()
    
    tx_signature = base64.b64encode(
        hashlib.sha256(f"solana_tx_{time.time()}".encode()).digest()
    ).decode()[:88]
    
    return {
        "success": True,
        "transaction_signature": tx_signature,
        "dna_hash": hashlib.sha256(b"test_dna").hexdigest()[:64],
        "creator": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "metadata_uri": "https://arweave.net/test_metadata",
        "cluster": "devnet",
        "test_mode": True,
        "timestamp": int(time.time())
    }

# ============================================================================
# BATCH OPERATIONS
# ============================================================================

@app.post("/test/batch/compute_dna")
async def batch_compute_dna(identifiers: List[str]):
    """Batch DNA Computation"""
    increment_request_count()
    
    results = [
        {
            "identifier": identifier,
            **generate_mock_dna(identifier),
            "success": True
        }
        for identifier in identifiers
    ]
    
    return {
        "success": True,
        "results": results,
        "count": len(results),
        "test_mode": True,
        "timestamp": int(time.time())
    }

@app.post("/test/batch/register_images")
async def batch_register_images(identifiers: List[str]):
    """Batch Image Registration"""
    increment_request_count()
    
    results = []
    for i, identifier in enumerate(identifiers):
        is_duplicate = identifier.endswith("_duplicate")
        dna_data = generate_mock_dna(identifier)
        
        results.append({
            "identifier": identifier,
            "success": not is_duplicate,
            "plagiarized": is_duplicate,
            "dna_hex": dna_data["dna_hex"],
            "image_id": f"batch_img_{i:03d}"
        })
    
    successful = sum(1 for r in results if r["success"])
    
    return {
        "success": True,
        "results": results,
        "total": len(results),
        "successful": successful,
        "duplicates": len(results) - successful,
        "test_mode": True,
        "timestamp": int(time.time())
    }

# ============================================================================
# UTILITY ENDPOINTS
# ============================================================================

@app.get("/test/scenarios")
async def test_scenarios():
    """Get predefined test scenarios"""
    return {
        "scenarios": {
            "unique_registration": {
                "endpoint": "/test/register_image",
                "method": "POST",
                "data": {
                    "image_identifier": "unique_test_001",
                    "image_id": "test_001",
                    "platform_id": "opensea"
                },
                "expected": {"success": True, "plagiarized": False}
            },
            "duplicate_detection": {
                "endpoint": "/test/register_image",
                "method": "POST",
                "data": {
                    "image_identifier": "unique_test_001_duplicate",
                    "image_id": "test_002",
                    "platform_id": "opensea"
                },
                "expected": {"success": False, "plagiarized": True}
            },
            "merkle_workflow": {
                "steps": [
                    {"endpoint": "/test/build_merkle", "method": "POST"},
                    {"endpoint": "/test/merkle_proof/{session_id}/5", "method": "GET"}
                ]
            }
        },
        "test_mode": True
    }

@app.get("/test/info")
async def test_info():
    """Test API Information"""
    return {
        "name": "TestSprite Mock API",
        "version": "1.0.0",
        "endpoints_available": 15,
        "request_count": request_count,
        "registered_images": len(registered_images),
        "merkle_sessions": len(merkle_sessions),
        "features": {
            "deterministic": True,
            "no_dependencies": True,
            "instant_response": True,
            "testsprite_ready": True
        },
        "test_mode": True
    }

@app.post("/test/reset")
async def reset_state():
    """Reset all state"""
    global request_count
    merkle_sessions.clear()
    registered_images.clear()
    request_count = 0
    
    return {
        "success": True,
        "message": "All state has been reset",
        "timestamp": int(time.time())
    }

# ============================================================================
# SERVER STARTUP
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    print("=" * 80)
    print("🧪 TestSprite Mock API Server")
    print("=" * 80)
    print("📍 Server: http://localhost:8000")
    print("📚 API Docs: http://localhost:8000/docs")
    print("🔍 Health: http://localhost:8000/health")
    print("✅ Endpoints: 15 testing endpoints available")
    print("🎯 TestSprite Ready: All endpoints support GET & POST")
    print("=" * 80)
    print("\nServer starting...")
    print()
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
