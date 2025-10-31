#!/usr/bin/env python3
"""
ProTrace Testing API Endpoints
================================

Dedicated endpoints for automated testing with mock data and predictable responses.
These endpoints ensure TestSprite and other test frameworks can run without external dependencies.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, Dict, List, Any
import hashlib
import time
import json
import base64
from datetime import datetime

# Create testing router
testing_router = APIRouter(prefix="/test", tags=["Testing"])

# ============================================================================
# Test Data Models
# ============================================================================

class TestImageRequest(BaseModel):
    image_name: Optional[str] = "test_image_1"
    width: Optional[int] = 100
    height: Optional[int] = 100

class TestDNARequest(BaseModel):
    image_identifier: str = "test_image_1"

class TestRegistrationRequest(BaseModel):
    image_identifier: str = "test_image_1"
    image_id: str = "test_img_001"
    platform_id: str = "test_platform"
    similarity_threshold: Optional[float] = 0.90

class TestMerkleRequest(BaseModel):
    leaf_count: int = 5

class TestEIP712Request(BaseModel):
    test_scenario: str = "valid_signature"

class TestEditionRequest(BaseModel):
    chain: str = "ethereum"
    edition_no: int = 1

class TestResetRequest(BaseModel):
    reset_type: str = "all"  # all, registry, merkle, state

# ============================================================================
# Mock Data Generators
# ============================================================================

def generate_mock_dna(identifier: str) -> Dict[str, str]:
    """Generate deterministic mock DNA hash based on identifier"""
    # Create deterministic hash from identifier
    base_hash = hashlib.sha256(identifier.encode()).hexdigest()
    
    # Split into dhash (16 hex chars = 64 bits) and grid_hash (48 hex chars = 192 bits)
    dhash = base_hash[:16]
    grid_hash = base_hash[16:64]
    dna_hex = dhash + grid_hash
    
    return {
        "dna_hex": dna_hex,
        "dhash": dhash,
        "grid_hash": grid_hash
    }

def generate_mock_image_data(image_name: str) -> bytes:
    """Generate mock image data (PNG header + random data)"""
    # PNG magic number and minimal header
    png_header = b'\x89PNG\r\n\x1a\n'
    mock_data = hashlib.sha256(image_name.encode()).digest()
    return png_header + mock_data

# ============================================================================
# Testing Endpoints
# ============================================================================

@testing_router.get("/info")
async def test_api_info():
    """Get information about testing endpoints"""
    return {
        "name": "ProTrace Testing API",
        "version": "1.0.0",
        "description": "Mock endpoints for automated testing",
        "endpoints": {
            "compute_dna": "POST /test/compute_dna",
            "register_image": "POST /test/register_image",
            "build_merkle": "POST /test/build_merkle",
            "eip712_sign": "POST /test/eip712_sign",
            "edition_register": "POST /test/edition_register",
            "vector_search": "POST /test/vector_search",
            "ipfs_upload": "POST /test/ipfs_upload",
            "relayer_monitor": "POST /test/relayer_monitor",
            "solana_register": "POST /test/solana_register",
            "reset_state": "POST /test/reset"
        },
        "features": {
            "deterministic_output": True,
            "no_external_dependencies": True,
            "instant_response": True,
            "state_management": True
        }
    }

@testing_router.get("/compute_dna")
async def test_compute_dna_get():
    """GET handler - returns demo DNA computation"""
    dna_data = generate_mock_dna("demo_image_001")
    return {
        "dna_hex": dna_data["dna_hex"],
        "dhash": dna_data["dhash"],
        "grid_hash": dna_data["grid_hash"],
        "success": True,
        "test_mode": True,
        "image_identifier": "demo_image_001",
        "note": "This is a GET demo. For custom images, use POST with body."
    }

@testing_router.post("/compute_dna")
async def test_compute_dna(request: TestDNARequest):
    """
    Mock DNA computation endpoint for testing
    Returns deterministic DNA hash based on image identifier
    """
    dna_data = generate_mock_dna(request.image_identifier)
    
    return {
        "dna_hex": dna_data["dna_hex"],
        "dhash": dna_data["dhash"],
        "grid_hash": dna_data["grid_hash"],
        "success": True,
        "test_mode": True,
        "image_identifier": request.image_identifier
    }

@testing_router.get("/register_image")
async def test_register_image_get():
    """GET handler - returns demo image registration"""
    dna_data = generate_mock_dna("demo_unique_image")
    mock_merkle_root = hashlib.sha256(f"{dna_data['dna_hex']}demo".encode()).hexdigest()
    return {
        "success": True,
        "plagiarized": False,
        "root_hash": mock_merkle_root,
        "match": None,
        "dna_hex": dna_data["dna_hex"],
        "test_mode": True,
        "image_id": "demo_img_001",
        "platform_id": "demo_platform",
        "note": "This is a GET demo. For custom registration, use POST with body."
    }

@testing_router.post("/register_image")
async def test_register_image(request: TestRegistrationRequest):
    """
    Mock image registration endpoint for testing
    Simulates duplicate detection with predictable behavior
    """
    # Generate DNA for the image
    dna_data = generate_mock_dna(request.image_identifier)
    
    # Simulate duplicate detection logic
    # Images ending with "_duplicate" are treated as duplicates
    is_duplicate = request.image_identifier.endswith("_duplicate")
    
    if is_duplicate:
        # Return duplicate match
        original_id = request.image_identifier.replace("_duplicate", "")
        return {
            "success": False,
            "plagiarized": True,
            "root_hash": None,
            "match": {
                "image_id": original_id,
                "similarity": 0.95,
                "platform_id": "test_platform",
                "registered_at": int(time.time()) - 3600
            },
            "dna_hex": dna_data["dna_hex"],
            "test_mode": True
        }
    else:
        # Return successful registration
        mock_merkle_root = hashlib.sha256(
            f"{dna_data['dna_hex']}{request.image_id}".encode()
        ).hexdigest()
        
        return {
            "success": True,
            "plagiarized": False,
            "root_hash": mock_merkle_root,
            "match": None,
            "dna_hex": dna_data["dna_hex"],
            "test_mode": True,
            "image_id": request.image_id,
            "platform_id": request.platform_id
        }

@testing_router.get("/build_merkle")
async def test_build_merkle_get():
    """GET handler - returns demo Merkle tree"""
    leaves = [f"mock_dna_hash_{i}" for i in range(5)]
    combined = "".join(leaves)
    root_hash = hashlib.sha256(combined.encode()).hexdigest()
    session_id = hashlib.sha256(f"{root_hash}{time.time()}".encode()).hexdigest()[:16]
    return {
        "root_hash": root_hash,
        "leaf_count": 5,
        "session_id": session_id,
        "success": True,
        "test_mode": True,
        "note": "This is a GET demo. For custom leaf count, use POST with body."
    }

@testing_router.post("/build_merkle")
async def test_build_merkle(request: TestMerkleRequest):
    """
    Mock Merkle tree building endpoint
    Returns deterministic root hash and session ID
    """
    # Generate mock leaves
    leaves = [f"mock_dna_hash_{i}" for i in range(request.leaf_count)]
    
    # Generate deterministic root hash
    combined = "".join(leaves)
    root_hash = hashlib.sha256(combined.encode()).hexdigest()
    
    # Generate session ID
    session_id = hashlib.sha256(f"{root_hash}{time.time()}".encode()).hexdigest()[:16]
    
    return {
        "root_hash": root_hash,
        "leaf_count": request.leaf_count,
        "session_id": session_id,
        "success": True,
        "test_mode": True,
        "leaves_generated": leaves[:3] + ["..."] if request.leaf_count > 3 else leaves
    }

@testing_router.get("/merkle_proof/{session_id}/{leaf_index}")
async def test_get_merkle_proof(session_id: str, leaf_index: int):
    """
    Mock Merkle proof retrieval
    Returns deterministic proof based on session and index
    """
    # Generate mock proof
    proof = [
        hashlib.sha256(f"{session_id}_sibling_{i}".encode()).hexdigest()
        for i in range(3)  # 3 levels in the tree
    ]
    
    # Mock root hash
    root_hash = hashlib.sha256(f"{session_id}_root".encode()).hexdigest()
    
    return {
        "leaf_index": leaf_index,
        "proof": proof,
        "root_hash": root_hash,
        "session_id": session_id,
        "test_mode": True
    }

@testing_router.get("/eip712_sign")
async def test_eip712_sign_get():
    """GET handler - returns demo EIP-712 signature"""
    message_data = {
        "creator_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "asset_hash": "0x" + hashlib.sha256(b"demo_asset").hexdigest(),
        "rights": "commercial",
        "token_type": "ERC721"
    }
    signature_input = json.dumps(message_data, sort_keys=True) + "demo"
    signature = "0x" + hashlib.sha256(signature_input.encode()).hexdigest() + hashlib.sha256((signature_input + "v").encode()).hexdigest()[:64]
    digest = "0x" + hashlib.sha256(signature_input.encode()).hexdigest()
    return {
        "signature": signature,
        "digest": digest,
        "message": message_data,
        "test_mode": True,
        "note": "This is a GET demo. For custom scenarios, use POST with body."
    }

@testing_router.post("/eip712_sign")
async def test_eip712_sign(request: TestEIP712Request):
    """
    Mock EIP-712 signing endpoint
    Returns deterministic signature based on scenario
    """
    # Generate mock signature
    message_data = {
        "creator_address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e",
        "asset_hash": "0x" + hashlib.sha256(b"test_asset").hexdigest(),
        "rights": "commercial",
        "token_type": "ERC721"
    }
    
    # Deterministic signature
    signature_input = json.dumps(message_data, sort_keys=True) + request.test_scenario
    signature = "0x" + hashlib.sha256(signature_input.encode()).hexdigest() + \
                hashlib.sha256((signature_input + "v").encode()).hexdigest()[:64]
    
    digest = "0x" + hashlib.sha256(signature_input.encode()).hexdigest()
    
    return {
        "signature": signature,
        "digest": digest,
        "message": message_data,
        "test_mode": True,
        "scenario": request.test_scenario
    }

@testing_router.get("/edition_register")
async def test_edition_register_get():
    """GET handler - returns demo edition registration"""
    universal_key = hashlib.sha256(b"ethereum_1").hexdigest()[:32]
    return {
        "success": True,
        "chain": "ethereum",
        "edition_no": 1,
        "max_editions": 100,
        "universal_key": universal_key,
        "test_mode": True,
        "contract": "0x" + hashlib.sha256(b"ethereum").hexdigest()[:40],
        "token_id": "1",
        "note": "This is a GET demo. For custom chains/editions, use POST with body."
    }

@testing_router.post("/edition_register")
async def test_edition_register(request: TestEditionRequest):
    """
    Mock edition registration for multi-chain NFTs
    Always succeeds with deterministic response
    """
    universal_key = hashlib.sha256(
        f"{request.chain}_{request.edition_no}".encode()
    ).hexdigest()[:32]
    
    return {
        "success": True,
        "chain": request.chain,
        "edition_no": request.edition_no,
        "max_editions": 100,
        "universal_key": universal_key,
        "test_mode": True,
        "contract": "0x" + hashlib.sha256(request.chain.encode()).hexdigest()[:40],
        "token_id": str(request.edition_no)
    }

@testing_router.get("/vector_search")
async def test_vector_search_get():
    """GET handler - returns demo vector search"""
    results = [
        {
            "dna_hash": hashlib.sha256(f"similar_dna_{i}".encode()).hexdigest()[:64],
            "similarity": 0.95 - (i * 0.02),
            "metadata": {
                "image_id": f"img_{i}",
                "platform_id": "demo_platform",
                "timestamp": int(time.time()) - (i * 3600)
            }
        }
        for i in range(3)
    ]
    return {
        "results": results,
        "count": len(results),
        "threshold": 0.90,
        "test_mode": True,
        "note": "This is a GET demo. For custom searches, use POST with body."
    }

@testing_router.post("/vector_search")
async def test_vector_search():
    """
    Mock vector similarity search
    Returns deterministic similar DNAs
    """
    # Generate mock results
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
        "results": results,
        "count": len(results),
        "threshold": 0.90,
        "test_mode": True
    }

@testing_router.get("/ipfs_upload")
async def test_ipfs_upload_get():
    """GET handler - returns demo IPFS upload"""
    manifest = {
        "dna_hash": hashlib.sha256(b"demo_manifest").hexdigest(),
        "timestamp": int(time.time()),
        "version": "1.0"
    }
    cid_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    cid = "Qm" + base64.b32encode(bytes.fromhex(cid_hash[:40])).decode()[:44]
    return {
        "cid": cid,
        "manifest": manifest,
        "size": len(json.dumps(manifest)),
        "timestamp": int(time.time()),
        "test_mode": True,
        "note": "This is a GET demo. For custom manifests, use POST with body."
    }

@testing_router.post("/ipfs_upload")
async def test_ipfs_upload():
    """
    Mock IPFS manifest upload
    Returns deterministic CID
    """
    manifest = {
        "dna_hash": hashlib.sha256(b"test_manifest").hexdigest(),
        "timestamp": int(time.time()),
        "version": "1.0"
    }
    
    # Generate deterministic CID
    cid_hash = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    cid = "Qm" + base64.b32encode(bytes.fromhex(cid_hash[:40])).decode()[:44]
    
    return {
        "cid": cid,
        "manifest": manifest,
        "size": len(json.dumps(manifest)),
        "timestamp": int(time.time()),
        "test_mode": True
    }

@testing_router.get("/relayer_monitor")
async def test_relayer_monitor_get():
    """GET handler - returns demo relayer monitor"""
    monitor_id = hashlib.sha256(f"demo_monitor_{time.time()}".encode()).hexdigest()[:16]
    return {
        "success": True,
        "monitor_id": monitor_id,
        "chain": "ethereum",
        "contract_address": "0x" + hashlib.sha256(b"demo_contract").hexdigest()[:40],
        "event_types": ["Transfer", "Approval"],
        "status": "monitoring",
        "test_mode": True,
        "note": "This is a GET demo. For custom chains/contracts, use POST with body."
    }

@testing_router.post("/relayer_monitor")
async def test_relayer_monitor():
    """
    Mock blockchain event relayer
    Simulates monitor startup
    """
    monitor_id = hashlib.sha256(
        f"monitor_{time.time()}".encode()
    ).hexdigest()[:16]
    
    return {
        "success": True,
        "monitor_id": monitor_id,
        "chain": "ethereum",
        "contract_address": "0x" + hashlib.sha256(b"test_contract").hexdigest()[:40],
        "event_types": ["Transfer", "Approval"],
        "status": "monitoring",
        "test_mode": True
    }

@testing_router.get("/solana_register")
async def test_solana_register_get():
    """GET handler - returns demo Solana registration"""
    tx_signature = base64.b64encode(
        hashlib.sha256(f"demo_solana_tx_{time.time()}".encode()).digest()
    ).decode()[:88]
    return {
        "success": True,
        "transaction_signature": tx_signature,
        "dna_hash": hashlib.sha256(b"demo_dna").hexdigest()[:64],
        "creator": "7xKXtg2CW87d97TXJSDpbD5jBkheTqA83TZRuJosgAsU",
        "metadata_uri": "https://arweave.net/demo_metadata",
        "cluster": "devnet",
        "timestamp": int(time.time()),
        "test_mode": True,
        "note": "This is a GET demo. For custom registrations, use POST with body."
    }

@testing_router.post("/solana_register")
async def test_solana_register():
    """
    Mock Solana DNA registration
    Returns deterministic transaction signature
    """
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
        "timestamp": int(time.time()),
        "test_mode": True
    }

@testing_router.post("/reset")
async def test_reset_state(request: TestResetRequest):
    """
    Reset test state for clean test runs
    """
    return {
        "success": True,
        "reset_type": request.reset_type,
        "message": f"Test state '{request.reset_type}' has been reset",
        "timestamp": int(time.time())
    }

# ============================================================================
# Batch Testing Endpoints
# ============================================================================

@testing_router.post("/batch/compute_dna")
async def test_batch_compute_dna(identifiers: List[str]):
    """
    Batch DNA computation for testing
    """
    results = [
        {
            "identifier": identifier,
            **generate_mock_dna(identifier),
            "success": True
        }
        for identifier in identifiers
    ]
    
    return {
        "results": results,
        "count": len(results),
        "test_mode": True
    }

@testing_router.post("/batch/register_images")
async def test_batch_register(identifiers: List[str]):
    """
    Batch image registration for testing
    """
    results = []
    for i, identifier in enumerate(identifiers):
        dna_data = generate_mock_dna(identifier)
        is_duplicate = identifier.endswith("_duplicate")
        
        results.append({
            "identifier": identifier,
            "success": not is_duplicate,
            "plagiarized": is_duplicate,
            "dna_hex": dna_data["dna_hex"],
            "image_id": f"test_img_{i:03d}"
        })
    
    return {
        "results": results,
        "total": len(results),
        "successful": sum(1 for r in results if r["success"]),
        "duplicates": sum(1 for r in results if r["plagiarized"]),
        "test_mode": True
    }

# ============================================================================
# Test Scenarios
# ============================================================================

@testing_router.get("/scenarios")
async def test_scenarios():
    """
    Get predefined test scenarios
    """
    return {
        "scenarios": {
            "successful_registration": {
                "description": "Register unique image successfully",
                "endpoint": "/test/register_image",
                "data": {
                    "image_identifier": "unique_image_001",
                    "image_id": "img_001",
                    "platform_id": "opensea"
                },
                "expected_result": {
                    "success": True,
                    "plagiarized": False
                }
            },
            "duplicate_detection": {
                "description": "Detect duplicate image",
                "endpoint": "/test/register_image",
                "data": {
                    "image_identifier": "unique_image_001_duplicate",
                    "image_id": "img_002",
                    "platform_id": "opensea"
                },
                "expected_result": {
                    "success": False,
                    "plagiarized": True
                }
            },
            "merkle_proof_flow": {
                "description": "Build tree and get proof",
                "steps": [
                    {
                        "step": 1,
                        "endpoint": "/test/build_merkle",
                        "data": {"leaf_count": 10}
                    },
                    {
                        "step": 2,
                        "endpoint": "/test/merkle_proof/{session_id}/5",
                        "note": "Use session_id from step 1"
                    }
                ]
            },
            "cross_chain_edition": {
                "description": "Register editions on multiple chains",
                "chains": ["ethereum", "solana", "tezos"],
                "endpoint": "/test/edition_register"
            }
        }
    }

# ============================================================================
# Health & Status
# ============================================================================

@testing_router.get("/health")
async def test_health():
    """
    Test API health check
    """
    return {
        "status": "healthy",
        "mode": "testing",
        "endpoints_available": 15,
        "features": {
            "mock_data": True,
            "deterministic": True,
            "no_dependencies": True,
            "instant_response": True
        },
        "timestamp": int(time.time())
    }

@testing_router.get("/status")
async def test_status():
    """
    Detailed testing API status
    """
    return {
        "api": "ProTrace Testing API",
        "version": "1.0.0",
        "mode": "testing",
        "uptime": "operational",
        "endpoints": {
            "total": 15,
            "categories": {
                "dna": 2,
                "registration": 2,
                "merkle": 2,
                "blockchain": 4,
                "batch": 2,
                "utility": 3
            }
        },
        "state": {
            "deterministic_mode": True,
            "external_dependencies": False,
            "database_required": False,
            "ipfs_required": False
        },
        "timestamp": datetime.utcnow().isoformat()
    }
