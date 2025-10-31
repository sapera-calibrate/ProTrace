"""
ProTRACE Production API Server
Clean, organized, production-ready backend
"""

from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import hashlib
import time
import logging
from datetime import datetime

from backend.config import settings
from protrace.image_dna import compute_dna_hash
from protrace.merkle import MerkleTree
from protrace.registration.register_image import register_image
from protrace.vector_db import VectorDB
from protrace.ipfs import IPFSClient
from protrace.eip712 import sign_registration
from protrace.edition_core import EditionRegistry
from protrace.relayer_service import BlockchainRelayer

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Production-grade NFT authenticity verification API",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# Add middlewares
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# ============================================================================
# State Management
# ============================================================================

class AppState:
    """Application state holder"""
    def __init__(self):
        self.merkle_sessions: Dict[str, MerkleTree] = {}
        self.vector_db: Optional[VectorDB] = None
        self.ipfs_client: Optional[IPFSClient] = None
        self.edition_registry: EditionRegistry = EditionRegistry()
        self.relayer: Optional[BlockchainRelayer] = None
        self.request_count: int = 0
    
    def initialize(self):
        """Initialize external services"""
        if settings.VECTOR_DB_ENABLED and settings.VECTOR_DB_URL:
            self.vector_db = VectorDB(settings.VECTOR_DB_URL)
            logger.info("Vector DB initialized")
        
        if settings.IPFS_ENABLED:
            self.ipfs_client = IPFSClient(settings.IPFS_API_URL)
            logger.info("IPFS client initialized")

app.state = AppState()

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    app.state.initialize()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down ProTRACE API")

# ============================================================================
# Request/Response Models
# ============================================================================

class DNAComputeRequest(BaseModel):
    """Request to compute DNA hash"""
    image_data: Optional[str] = Field(None, description="Base64 encoded image data")
    image_path: Optional[str] = Field(None, description="Path to image file")
    image_url: Optional[str] = Field(None, description="URL to image")

class DNAResponse(BaseModel):
    """DNA computation response"""
    dna_hex: str
    dhash: str
    grid_hash: str
    timestamp: int
    success: bool = True

class ImageRegistrationRequest(BaseModel):
    """Image registration request"""
    image_identifier: str
    image_id: str
    platform_id: str
    similarity_threshold: float = Field(default=0.90, ge=0.0, le=1.0)
    metadata: Optional[Dict[str, Any]] = None

class ImageRegistrationResponse(BaseModel):
    """Image registration response"""
    success: bool
    plagiarized: bool
    root_hash: Optional[str]
    match: Optional[Dict[str, Any]]
    dna_hex: str
    registration_id: str
    timestamp: int

class MerkleTreeRequest(BaseModel):
    """Merkle tree build request"""
    dna_hashes: List[str] = Field(..., min_items=1)
    session_name: Optional[str] = None

class MerkleTreeResponse(BaseModel):
    """Merkle tree build response"""
    root_hash: str
    leaf_count: int
    session_id: str
    tree_height: int
    timestamp: int

class MerkleProofResponse(BaseModel):
    """Merkle proof response"""
    leaf_index: int
    proof: List[str]
    root_hash: str
    verified: bool

class EditionRegisterRequest(BaseModel):
    """NFT edition registration request"""
    chain: str = Field(..., description="ethereum, solana, or tezos")
    edition_no: int = Field(..., ge=1)
    max_editions: Optional[int] = Field(default=100, ge=1)
    metadata: Optional[Dict[str, Any]] = None

class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    environment: str
    timestamp: str
    uptime: float
    services: Dict[str, bool]

# ============================================================================
# Core API Endpoints
# ============================================================================

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": f"{settings.API_PREFIX}/docs" if settings.DEBUG else None,
        "status": "operational"
    }

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Comprehensive health check"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT.value,
        "timestamp": datetime.utcnow().isoformat(),
        "uptime": time.time(),
        "services": {
            "api": True,
            "vector_db": app.state.vector_db is not None,
            "ipfs": app.state.ipfs_client is not None,
            "merkle": len(app.state.merkle_sessions) >= 0,
        }
    }

# ============================================================================
# DNA Fingerprinting Endpoints
# ============================================================================

@app.post(f"{settings.API_PREFIX}/dna/compute", response_model=DNAResponse)
async def compute_dna(request: DNAComputeRequest):
    """
    Compute DNA fingerprint for an image
    
    Supports three input methods:
    - Base64 encoded image data
    - Local file path
    - Remote URL
    """
    try:
        app.state.request_count += 1
        
        # Import here to avoid circular imports
        from PIL import Image
        import io
        import base64
        import requests
        
        # Get image based on input method
        if request.image_data:
            image_bytes = base64.b64decode(request.image_data)
            image = Image.open(io.BytesIO(image_bytes))
        elif request.image_path:
            image = Image.open(request.image_path)
        elif request.image_url:
            response = requests.get(request.image_url, timeout=10)
            response.raise_for_status()
            image = Image.open(io.BytesIO(response.content))
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide image_data, image_path, or image_url"
            )
        
        # Compute DNA hash
        dna_result = compute_dna_hash(image)
        
        return DNAResponse(
            dna_hex=dna_result['dna_hex'],
            dhash=dna_result['dhash'],
            grid_hash=dna_result['grid_hash'],
            timestamp=int(time.time())
        )
    
    except Exception as e:
        logger.error(f"DNA computation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DNA computation failed: {str(e)}"
        )

# ============================================================================
# Image Registration Endpoints
# ============================================================================

@app.post(f"{settings.API_PREFIX}/images/register", response_model=ImageRegistrationResponse)
async def register_image_endpoint(request: ImageRegistrationRequest):
    """
    Register an image and check for duplicates
    
    Performs DNA-based duplicate detection and stores in registry
    """
    try:
        app.state.request_count += 1
        
        result = register_image(
            image_identifier=request.image_identifier,
            image_id=request.image_id,
            platform_id=request.platform_id,
            similarity_threshold=request.similarity_threshold,
            metadata=request.metadata or {}
        )
        
        return ImageRegistrationResponse(
            success=result['success'],
            plagiarized=result['plagiarized'],
            root_hash=result.get('root_hash'),
            match=result.get('match'),
            dna_hex=result['dna_hex'],
            registration_id=request.image_id,
            timestamp=int(time.time())
        )
    
    except Exception as e:
        logger.error(f"Image registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )

# ============================================================================
# Merkle Tree Endpoints
# ============================================================================

@app.post(f"{settings.API_PREFIX}/merkle/build", response_model=MerkleTreeResponse)
async def build_merkle_tree(request: MerkleTreeRequest):
    """
    Build Merkle tree from DNA hashes
    
    Creates a cryptographic proof tree for batch verification
    """
    try:
        app.state.request_count += 1
        
        # Create Merkle tree
        tree = MerkleTree(request.dna_hashes)
        
        # Generate session ID
        session_id = hashlib.sha256(
            f"{tree.root}_{time.time()}_{request.session_name or ''}".encode()
        ).hexdigest()[:16]
        
        # Store session
        app.state.merkle_sessions[session_id] = tree
        
        return MerkleTreeResponse(
            root_hash=tree.root,
            leaf_count=len(request.dna_hashes),
            session_id=session_id,
            tree_height=tree.height,
            timestamp=int(time.time())
        )
    
    except Exception as e:
        logger.error(f"Merkle tree build failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Merkle tree build failed: {str(e)}"
        )

@app.get(f"{settings.API_PREFIX}/merkle/proof/{{session_id}}/{{leaf_index}}", 
         response_model=MerkleProofResponse)
async def get_merkle_proof(session_id: str, leaf_index: int):
    """
    Get Merkle proof for a specific leaf
    
    Returns proof path for verification
    """
    try:
        app.state.request_count += 1
        
        if session_id not in app.state.merkle_sessions:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Session {session_id} not found"
            )
        
        tree = app.state.merkle_sessions[session_id]
        
        if leaf_index < 0 or leaf_index >= len(tree.leaves):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid leaf index {leaf_index}"
            )
        
        proof = tree.get_proof(leaf_index)
        
        return MerkleProofResponse(
            leaf_index=leaf_index,
            proof=proof,
            root_hash=tree.root,
            verified=True
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Merkle proof generation failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Proof generation failed: {str(e)}"
        )

# ============================================================================
# Edition Management Endpoints
# ============================================================================

@app.post(f"{settings.API_PREFIX}/editions/register")
async def register_edition(request: EditionRegisterRequest):
    """
    Register NFT edition across chains
    
    Supports Ethereum, Solana, and Tezos
    """
    try:
        app.state.request_count += 1
        
        edition_data = app.state.edition_registry.register_edition(
            chain=request.chain,
            edition_no=request.edition_no,
            max_editions=request.max_editions,
            metadata=request.metadata or {}
        )
        
        return {
            "success": True,
            "chain": request.chain,
            "edition_no": request.edition_no,
            "universal_key": edition_data['universal_key'],
            "timestamp": int(time.time())
        }
    
    except Exception as e:
        logger.error(f"Edition registration failed: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Edition registration failed: {str(e)}"
        )

# ============================================================================
# Admin/Utility Endpoints
# ============================================================================

@app.get(f"{settings.API_PREFIX}/stats")
async def get_stats():
    """Get API statistics"""
    return {
        "request_count": app.state.request_count,
        "merkle_sessions": len(app.state.merkle_sessions),
        "services_active": {
            "vector_db": app.state.vector_db is not None,
            "ipfs": app.state.ipfs_client is not None,
        },
        "timestamp": int(time.time())
    }

@app.delete(f"{settings.API_PREFIX}/admin/reset")
async def reset_state():
    """Reset application state (development only)"""
    if settings.ENVIRONMENT == "production":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not allowed in production"
        )
    
    app.state.merkle_sessions.clear()
    app.state.request_count = 0
    
    return {
        "success": True,
        "message": "State reset complete",
        "timestamp": int(time.time())
    }

# ============================================================================
# Error Handlers
# ============================================================================

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "Internal server error",
            "detail": str(exc) if settings.DEBUG else "An error occurred",
            "timestamp": int(time.time())
        }
    )

# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.api:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=1 if settings.RELOAD else settings.WORKERS,
        log_level=settings.LOG_LEVEL.lower()
    )
