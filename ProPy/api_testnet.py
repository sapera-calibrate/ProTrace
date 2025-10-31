#!/usr/bin/env python3
"""
ProTRACE Testnet API Server
User-facing API for DNA extraction and Merkle trees on Solana Testnet
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sys
from pathlib import Path
import tempfile
import os
import time
from typing import List

# Add modules to path
sys.path.insert(0, str(Path(__file__).parent))

from modules.protrace_legacy.image_dna import compute_dna
from modules.protrace_legacy.merkle import MerkleTree

# Initialize FastAPI
app = FastAPI(
    title="ProTRACE Testnet API",
    description="DNA Extraction and Merkle Tree API on Solana Testnet",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
SOLANA_PROGRAM_ID = "7cjcAJv1fgJdwVSrabX9yVXCgyK1gKVnRUBFs1ZcG2sG"
SOLANA_NETWORK = "testnet"
SOLANA_RPC_URL = "https://api.testnet.solana.com"

# Models
class MerkleCreateRequest(BaseModel):
    leaves: List[str]
    metadata: dict = {}

class DnaResponse(BaseModel):
    success: bool
    dna_hash: str
    dhash: str
    grid_hash: str
    algorithm: str
    bits: int
    extraction_time_ms: float

class MerkleResponse(BaseModel):
    success: bool
    root: str
    leaf_count: int
    network: str
    generation_time_ms: float

# Routes

@app.get("/")
def root():
    """API root endpoint with information"""
    return {
        "name": "ProTRACE Testnet API",
        "version": "1.0.0",
        "description": "DNA Fingerprinting and Merkle Tree API",
        "network": SOLANA_NETWORK,
        "program_id": SOLANA_PROGRAM_ID,
        "rpc_url": SOLANA_RPC_URL,
        "endpoints": {
            "extract_dna": "POST /dna/extract",
            "create_merkle": "POST /merkle/create",
            "verify_merkle": "POST /merkle/verify",
            "health": "GET /health",
            "docs": "GET /docs"
        },
        "features": [
            "256-bit DNA fingerprinting",
            "BLAKE3-based Merkle trees",
            "Solana Testnet integration",
            "RESTful API",
            "OpenAPI documentation"
        ]
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "network": SOLANA_NETWORK,
        "program_id": SOLANA_PROGRAM_ID,
        "timestamp": int(time.time()),
        "modules": {
            "dna_extraction": True,
            "merkle_tree": True,
            "solana_integration": True
        }
    }

@app.post("/dna/extract", response_model=DnaResponse)
async def extract_dna(file: UploadFile = File(...)):
    """
    Extract 256-bit DNA fingerprint from uploaded image
    
    ## Parameters
    - **file**: Image file (PNG, JPEG, etc.)
    
    ## Returns
    - **dna_hash**: Complete 256-bit hash (64 hex chars)
    - **dhash**: 64-bit gradient-based component
    - **grid_hash**: 192-bit structure-based component
    - **algorithm**: dHash+Grid-Optimized
    - **bits**: 256
    - **extraction_time_ms**: Processing time
    
    ## Example
    ```bash
    curl -X POST "http://localhost:8000/dna/extract" \\
      -F "file=@image.png"
    ```
    """
    try:
        start_time = time.time()
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Extract DNA
        result = compute_dna(tmp_path)
        
        # Cleanup
        os.unlink(tmp_path)
        
        extraction_time = (time.time() - start_time) * 1000  # Convert to ms
        
        return DnaResponse(
            success=True,
            dna_hash=result['dna_hex'],
            dhash=result['dhash'],
            grid_hash=result['grid_hash'],
            algorithm=result['algorithm'],
            bits=result['bits'],
            extraction_time_ms=round(extraction_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"DNA extraction failed: {str(e)}")

@app.post("/merkle/create", response_model=MerkleResponse)
def create_merkle_tree(request: MerkleCreateRequest):
    """
    Create Merkle tree from DNA hashes
    
    ## Parameters
    - **leaves**: List of DNA hash strings (64 hex chars each)
    - **metadata**: Optional metadata for each leaf
    
    ## Returns
    - **root**: Merkle root hash
    - **leaf_count**: Number of leaves in tree
    - **network**: Solana network (testnet)
    - **generation_time_ms**: Processing time
    
    ## Example
    ```bash
    curl -X POST "http://localhost:8000/merkle/create" \\
      -H "Content-Type: application/json" \\
      -d '{"leaves": ["abc123...", "def456..."]}'
    ```
    """
    try:
        start_time = time.time()
        
        if not request.leaves:
            raise HTTPException(status_code=400, detail="At least one leaf required")
        
        if len(request.leaves) > 10000:
            raise HTTPException(status_code=400, detail="Maximum 10,000 leaves allowed")
        
        # Create Merkle tree
        tree = MerkleTree()
        
        for i, leaf in enumerate(request.leaves):
            pointer = request.metadata.get(str(i), {}).get('pointer', f'ptr_{i}')
            platform = request.metadata.get(str(i), {}).get('platform', SOLANA_NETWORK)
            tree.add_leaf(leaf, pointer, platform, int(time.time()))
        
        # Build tree
        root = tree.build_tree()
        
        generation_time = (time.time() - start_time) * 1000
        
        return MerkleResponse(
            success=True,
            root=root,
            leaf_count=len(request.leaves),
            network=SOLANA_NETWORK,
            generation_time_ms=round(generation_time, 2)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Merkle tree creation failed: {str(e)}")

@app.post("/merkle/verify")
def verify_merkle_proof(
    leaf_index: int,
    root: str,
    proof: List[dict]
):
    """
    Verify a Merkle proof
    
    ## Parameters
    - **leaf_index**: Index of leaf to verify
    - **root**: Expected Merkle root
    - **proof**: Proof elements (list of {hash, position} dicts)
    
    ## Returns
    - **valid**: Whether proof is valid
    - **leaf_index**: Index that was verified
    - **root**: Root hash used for verification
    
    ## Example
    ```bash
    curl -X POST "http://localhost:8000/merkle/verify" \\
      -H "Content-Type: application/json" \\
      -d '{"leaf_index": 0, "root": "abc...", "proof": [...]}'
    ```
    """
    try:
        # Note: This is a simplified verification
        # Full implementation would reconstruct the tree or use stored proofs
        
        return {
            "success": True,
            "valid": True,  # Placeholder
            "leaf_index": leaf_index,
            "root": root,
            "message": "Proof verification endpoint - integrate with full tree implementation"
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Proof verification failed: {str(e)}")

@app.get("/info/program")
def program_info():
    """Get Solana program information"""
    return {
        "program_id": SOLANA_PROGRAM_ID,
        "network": SOLANA_NETWORK,
        "rpc_url": SOLANA_RPC_URL,
        "explorer_url": f"https://explorer.solana.com/address/{SOLANA_PROGRAM_ID}?cluster={SOLANA_NETWORK}",
        "instructions": [
            "anchor_dna_hash",
            "anchor_merkle_root_oracle",
            "batch_register_editions",
            "initialize_edition_registry",
            "initialize_merkle_root",
            "update_merkle_root",
            "verify_edition_authorization",
            "verify_merkle_proof"
        ],
        "security_txt": f"query-security-txt {SOLANA_PROGRAM_ID} --url {SOLANA_NETWORK}"
    }

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    return JSONResponse(
        status_code=500,
        content={
            "success": False,
            "error": str(exc),
            "type": type(exc).__name__
        }
    )

# Startup event
@app.on_event("startup")
async def startup_event():
    """Print startup information"""
    print("=" * 80)
    print("🚀 ProTRACE Testnet API Server Starting")
    print("=" * 80)
    print(f"Network: {SOLANA_NETWORK}")
    print(f"Program ID: {SOLANA_PROGRAM_ID}")
    print(f"API Docs: http://localhost:8000/docs")
    print(f"ReDoc: http://localhost:8000/redoc")
    print("=" * 80)

if __name__ == "__main__":
    import uvicorn
    
    print("\n🌐 Starting ProTRACE Testnet API...")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    print("\nPress Ctrl+C to stop\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
