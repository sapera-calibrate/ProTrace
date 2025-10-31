#!/usr/bin/env python3
"""
ProTrace Development API Server
================================

FastAPI server for testing ProTrace functionality.
Default port: 8000
"""

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, List
import uvicorn
import tempfile
import os
from pathlib import Path
import time

# Import ProTrace modules
try:
    from protrace.image_dna import compute_dna, dna_similarity, is_duplicate
    from protrace.merkle import MerkleTree, compute_leaf_hash
    from protrace import __version__
except ImportError as e:
    print(f"Warning: Could not import protrace modules: {e}")
    __version__ = "2.0.0"

app = FastAPI(
    title="ProTrace API",
    description="Digital Asset Verification System",
    version=__version__
)

# Request/Response Models
class DNARequest(BaseModel):
    image_path: str

class DNAResponse(BaseModel):
    dna_hex: str
    dhash: str
    grid_hash: str
    success: bool

class SimilarityRequest(BaseModel):
    dna1: str
    dna2: str

class SimilarityResponse(BaseModel):
    similarity: float
    is_duplicate: bool
    threshold: float

class RegistrationRequest(BaseModel):
    image_id: str
    platform_id: str
    similarity_threshold: Optional[float] = 0.90

class HealthResponse(BaseModel):
    status: str
    version: str
    service: str

# Health check endpoint
@app.get("/", response_model=HealthResponse)
@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "version": __version__,
        "service": "ProTrace API"
    }

# DNA Computation endpoint
@app.post("/api/v1/dna/compute", response_model=DNAResponse)
async def compute_dna_endpoint(request: DNARequest):
    """
    Compute DNA fingerprint for an image
    
    Args:
        request: DNARequest with image_path
        
    Returns:
        DNAResponse with DNA fingerprint
    """
    try:
        if not os.path.exists(request.image_path):
            raise HTTPException(status_code=404, detail="Image file not found")
        
        result = compute_dna(request.image_path)
        
        return {
            "dna_hex": result.get('dna_hex', ''),
            "dhash": result.get('dhash', ''),
            "grid_hash": result.get('grid_hash', ''),
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# DNA Comparison endpoint
@app.post("/api/v1/dna/compare", response_model=SimilarityResponse)
async def compare_dna_endpoint(request: SimilarityRequest):
    """
    Compare two DNA fingerprints
    
    Args:
        request: SimilarityRequest with two DNA hashes
        
    Returns:
        SimilarityResponse with similarity score
    """
    try:
        similarity = dna_similarity(request.dna1, request.dna2)
        threshold = 0.90
        is_dup = is_duplicate(request.dna1, request.dna2, threshold)
        
        return {
            "similarity": similarity,
            "is_duplicate": is_dup,
            "threshold": threshold
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Upload and compute DNA endpoint
@app.post("/api/v1/dna/upload")
async def upload_and_compute_dna(file: UploadFile = File(...)):
    """
    Upload an image and compute its DNA
    
    Args:
        file: Image file
        
    Returns:
        DNA fingerprint
    """
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
            content = await file.read()
            tmp.write(content)
            tmp_path = tmp.name
        
        # Compute DNA
        result = compute_dna(tmp_path)
        
        # Clean up
        os.unlink(tmp_path)
        
        return {
            "filename": file.filename,
            "dna_hex": result.get('dna_hex', ''),
            "dhash": result.get('dhash', ''),
            "grid_hash": result.get('grid_hash', ''),
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Merkle Tree endpoint
@app.post("/api/v1/merkle/build")
async def build_merkle_tree(leaves: List[str]):
    """
    Build a Merkle tree from DNA hashes
    
    Args:
        leaves: List of DNA hash strings
        
    Returns:
        Merkle root hash
    """
    try:
        tree = MerkleTree()
        
        # Add leaves
        for i, leaf in enumerate(leaves):
            tree.add_leaf(leaf, f"img_{i}", "test_platform", int(time.time()))
        
        # Build tree
        root_hash = tree.build_tree()
        
        return {
            "root_hash": root_hash,
            "leaf_count": len(leaves),
            "success": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Get Merkle proof endpoint
@app.get("/api/v1/merkle/proof/{leaf_index}")
async def get_merkle_proof(leaf_index: int):
    """
    Get Merkle proof for a leaf at given index
    
    Args:
        leaf_index: Index of the leaf
        
    Returns:
        Merkle proof
    """
    try:
        # This would need to maintain state - simplified for demo
        return {
            "leaf_index": leaf_index,
            "proof": [],
            "note": "Merkle tree state management required for production"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# API Info endpoint
@app.get("/api/v1/info")
async def api_info():
    """Get API information and available endpoints"""
    return {
        "name": "ProTrace API",
        "version": __version__,
        "endpoints": {
            "health": "GET /health",
            "compute_dna": "POST /api/v1/dna/compute",
            "compare_dna": "POST /api/v1/dna/compare",
            "upload_dna": "POST /api/v1/dna/upload",
            "build_merkle": "POST /api/v1/merkle/build",
            "get_proof": "GET /api/v1/merkle/proof/{leaf_index}"
        },
        "documentation": "/docs"
    }

# Test endpoint for TestSprite
@app.get("/api/v1/test")
async def test_endpoint():
    """Test endpoint for automated testing"""
    return {
        "status": "ok",
        "message": "ProTrace API is operational",
        "timestamp": str(time.time())
    }

def main():
    """Run the development server"""
    print("🚀 Starting ProTrace API Server...")
    print("📍 Server running at: http://localhost:8000")
    print("📚 API Documentation: http://localhost:8000/docs")
    print("🔍 Health Check: http://localhost:8000/health")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )

if __name__ == "__main__":
    main()
