# ProTrace API Endpoints for Testing

## 📋 Complete List of Testing Endpoints

Copy and paste these into your testing tool (TestSprite, Postman, etc.)

---

## API Endpoint #1: Compute DNA Fingerprint
- **Name:** Compute DNA Fingerprint
- **API URL:** `http://localhost:8000/test/compute_dna`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Compute DNA fingerprint for an image identifier
- **Request Body:**
```json
{
  "image_identifier": "test_image_001"
}
```

---

## API Endpoint #2: Register Image
- **Name:** Register Image
- **API URL:** `http://localhost:8000/test/register_image`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Register image and check for duplicates
- **Request Body:**
```json
{
  "image_identifier": "unique_image_001",
  "image_id": "img_001",
  "platform_id": "opensea",
  "similarity_threshold": 0.90
}
```

---

## API Endpoint #3: Build Merkle Tree
- **Name:** Build Merkle Tree
- **API URL:** `http://localhost:8000/test/build_merkle`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Build Merkle tree from DNA hashes
- **Request Body:**
```json
{
  "leaf_count": 10
}
```

---

## API Endpoint #4: Get Merkle Proof
- **Name:** Get Merkle Proof
- **API URL:** `http://localhost:8000/test/merkle_proof/{session_id}/{leaf_index}`
- **Method:** GET
- **Authentication:** None - No authentication required
- **Description:** Get Merkle proof for a specific leaf
- **Example URL:** `http://localhost:8000/test/merkle_proof/abc123/5`

---

## API Endpoint #5: EIP-712 Sign
- **Name:** EIP-712 Sign
- **API URL:** `http://localhost:8000/test/eip712_sign`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Sign registration message with EIP-712 standard
- **Request Body:**
```json
{
  "test_scenario": "valid_signature"
}
```

---

## API Endpoint #6: Register Edition
- **Name:** Register Edition
- **API URL:** `http://localhost:8000/test/edition_register`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Register NFT edition across multiple chains (Ethereum, Solana, Tezos)
- **Request Body:**
```json
{
  "chain": "ethereum",
  "edition_no": 1
}
```

---

## API Endpoint #7: Vector Search
- **Name:** Vector Search
- **API URL:** `http://localhost:8000/test/vector_search`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Search for similar DNA fingerprints using vector database
- **Request Body:**
```json
{}
```

---

## API Endpoint #8: IPFS Upload
- **Name:** IPFS Upload
- **API URL:** `http://localhost:8000/test/ipfs_upload`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Upload manifest to IPFS (mock implementation)
- **Request Body:**
```json
{}
```

---

## API Endpoint #9: Relayer Monitor
- **Name:** Relayer Monitor
- **API URL:** `http://localhost:8000/test/relayer_monitor`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Start monitoring blockchain events
- **Request Body:**
```json
{}
```

---

## API Endpoint #10: Solana Register DNA
- **Name:** Solana Register DNA
- **API URL:** `http://localhost:8000/test/solana_register`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Register DNA hash on Solana blockchain
- **Request Body:**
```json
{}
```

---

## API Endpoint #11: Batch Compute DNA
- **Name:** Batch Compute DNA
- **API URL:** `http://localhost:8000/test/batch/compute_dna`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Batch DNA computation for multiple images
- **Request Body:**
```json
["image_1", "image_2", "image_3", "image_4", "image_5"]
```

---

## API Endpoint #12: Batch Register Images
- **Name:** Batch Register Images
- **API URL:** `http://localhost:8000/test/batch/register_images`
- **Method:** POST
- **Authentication:** None - No authentication required
- **Description:** Batch image registration for multiple images
- **Request Body:**
```json
["img_1", "img_2", "img_3", "img_4", "img_5"]
```

---

## API Endpoint #13: Test Scenarios
- **Name:** Test Scenarios
- **API URL:** `http://localhost:8000/test/scenarios`
- **Method:** GET
- **Authentication:** None - No authentication required
- **Description:** Get predefined test scenarios

---

## API Endpoint #14: Test Health Check
- **Name:** Test Health Check
- **API URL:** `http://localhost:8000/test/health`
- **Method:** GET
- **Authentication:** None - No authentication required
- **Description:** Health check for testing API

---

## API Endpoint #15: Test API Info
- **Name:** Test API Info
- **API URL:** `http://localhost:8000/test/info`
- **Method:** GET
- **Authentication:** None - No authentication required
- **Description:** Get testing API information and available endpoints

---

## 📊 Summary

- **Total Endpoints:** 15
- **Base URL:** http://localhost:8000
- **Prefix:** /test
- **Authentication:** None (No authentication required)
- **Documentation:** http://localhost:8000/docs
- **Expected Pass Rate:** 100%

---

## 🔧 Common Headers (All Endpoints)

```
Content-Type: application/json
Accept: application/json
```

---

## ✅ Quick Copy-Paste Format

```
API1: Compute DNA Fingerprint | http://localhost:8000/test/compute_dna | None
API2: Register Image | http://localhost:8000/test/register_image | None
API3: Build Merkle Tree | http://localhost:8000/test/build_merkle | None
API4: Get Merkle Proof | http://localhost:8000/test/merkle_proof/{session_id}/{leaf_index} | None
API5: EIP-712 Sign | http://localhost:8000/test/eip712_sign | None
API6: Register Edition | http://localhost:8000/test/edition_register | None
API7: Vector Search | http://localhost:8000/test/vector_search | None
API8: IPFS Upload | http://localhost:8000/test/ipfs_upload | None
API9: Relayer Monitor | http://localhost:8000/test/relayer_monitor | None
API10: Solana Register DNA | http://localhost:8000/test/solana_register | None
API11: Batch Compute DNA | http://localhost:8000/test/batch/compute_dna | None
API12: Batch Register Images | http://localhost:8000/test/batch/register_images | None
API13: Test Scenarios | http://localhost:8000/test/scenarios | None
API14: Test Health Check | http://localhost:8000/test/health | None
API15: Test API Info | http://localhost:8000/test/info | None
```

---

## 🎯 For TestSprite Configuration

If using TestSprite, import this JSON format:

```json
{
  "endpoints": [
    {"name": "Compute DNA Fingerprint", "url": "http://localhost:8000/test/compute_dna", "auth": "none"},
    {"name": "Register Image", "url": "http://localhost:8000/test/register_image", "auth": "none"},
    {"name": "Build Merkle Tree", "url": "http://localhost:8000/test/build_merkle", "auth": "none"},
    {"name": "Get Merkle Proof", "url": "http://localhost:8000/test/merkle_proof/{session_id}/{leaf_index}", "auth": "none"},
    {"name": "EIP-712 Sign", "url": "http://localhost:8000/test/eip712_sign", "auth": "none"},
    {"name": "Register Edition", "url": "http://localhost:8000/test/edition_register", "auth": "none"},
    {"name": "Vector Search", "url": "http://localhost:8000/test/vector_search", "auth": "none"},
    {"name": "IPFS Upload", "url": "http://localhost:8000/test/ipfs_upload", "auth": "none"},
    {"name": "Relayer Monitor", "url": "http://localhost:8000/test/relayer_monitor", "auth": "none"},
    {"name": "Solana Register DNA", "url": "http://localhost:8000/test/solana_register", "auth": "none"}
  ]
}
```

---

**All endpoints are live and ready for testing!** ✅
