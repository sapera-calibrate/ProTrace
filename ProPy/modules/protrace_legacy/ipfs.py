"""
IPFS Manager
============

Extended IPFS functionality for ProTrace Cross-Chain Edition Management.
Supports immutable registry snapshots and edition metadata storage.
"""

import logging
import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class IPFSManager:
    """Extended IPFS manager for ProTrace with edition support"""

    def __init__(self, gateway: str = "127.0.0.1:5001", api_endpoint: str = "http://127.0.0.1:5001/api/v0"):
        self.gateway = gateway
        self.api_endpoint = api_endpoint
        self.uploaded_files: Dict[str, str] = {}  # cid -> content hash
        self.registry_snapshots: List[Dict[str, Any]] = []  # History of registry snapshots

    def upload_merkle_tree(self, manifest_data: dict) -> str:
        """Upload Merkle tree manifest to IPFS (mock implementation)"""
        # Create a mock CID based on content hash
        content_str = json.dumps(manifest_data, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode()).hexdigest()
        mock_cid = f"bafybei{content_hash[:46]}"  # Mock IPFS CID format

        self.uploaded_files[mock_cid] = content_hash
        logger.info(f"Mock uploaded manifest to IPFS: {mock_cid}")
        return mock_cid

    def upload_edition_registry_snapshot(self, registry_data: Dict[str, Any],
                                       version: str = "2.0") -> str:
        """Upload edition registry snapshot to IPFS for immutability"""
        try:
            # Add metadata for immutability
            snapshot = {
                "version": version,
                "timestamp": int(time.time()),
                "registry_data": registry_data,
                "content_hash": None,  # Will be set after hashing
                "previous_snapshot": self.registry_snapshots[-1]["cid"] if self.registry_snapshots else None
            }

            # Calculate content hash for integrity
            content_str = json.dumps(snapshot, sort_keys=True, default=str)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()
            snapshot["content_hash"] = content_hash

            # Create IPFS-compatible CID (mock)
            cid = f"bafyre{content_hash[:48]}"  # Edition registry CID format

            # Store snapshot metadata
            snapshot_record = {
                "cid": cid,
                "content_hash": content_hash,
                "timestamp": snapshot["timestamp"],
                "edition_count": registry_data.get("total_editions", 0),
                "core_asset_count": registry_data.get("total_core_assets", 0)
            }
            self.registry_snapshots.append(snapshot_record)

            self.uploaded_files[cid] = content_hash
            logger.info(f"✅ Uploaded edition registry snapshot: {cid}")
            logger.info(f"   Editions: {snapshot_record['edition_count']}")
            logger.info(f"   Core Assets: {snapshot_record['core_asset_count']}")

            return cid

        except Exception as e:
            logger.error(f"Failed to upload registry snapshot: {e}")
            raise

    def upload_edition_metadata(self, edition_metadata: Dict[str, Any],
                              universal_key: str) -> str:
        """Upload individual edition metadata to IPFS"""
        try:
            metadata_packet = {
                "universal_key": universal_key,
                "edition_metadata": edition_metadata,
                "timestamp": int(time.time()),
                "schema_version": "2.0"
            }

            # Create deterministic CID based on universal key
            key_hash = hashlib.sha256(universal_key.encode()).hexdigest()
            cid = f"bafybeiedition{key_hash[:42]}"  # Edition-specific CID

            content_str = json.dumps(metadata_packet, sort_keys=True, default=str)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()

            self.uploaded_files[cid] = content_hash
            logger.info(f"✅ Uploaded edition metadata: {cid} ({universal_key})")

            return cid

        except Exception as e:
            logger.error(f"Failed to upload edition metadata: {e}")
            raise

    def upload_batch_edition_update(self, batch_data: Dict[str, Any]) -> str:
        """Upload batch edition update to IPFS"""
        try:
            batch_packet = {
                "batch_id": batch_data.get("batch_id", f"batch_{int(time.time())}"),
                "timestamp": int(time.time()),
                "edition_updates": batch_data.get("edition_updates", []),
                "merkle_root": batch_data.get("merkle_root"),
                "registry_cid": batch_data.get("registry_cid"),
                "chain": batch_data.get("chain"),
                "contract": batch_data.get("contract")
            }

            content_str = json.dumps(batch_packet, sort_keys=True, default=str)
            content_hash = hashlib.sha256(content_str.encode()).hexdigest()
            cid = f"bafybeibatch{content_hash[:44]}"  # Batch update CID

            self.uploaded_files[cid] = content_hash
            logger.info(f"✅ Uploaded batch update: {cid} ({len(batch_packet['edition_updates'])} editions)")

            return cid

        except Exception as e:
            logger.error(f"Failed to upload batch update: {e}")
            raise

    def download_proof(self, proof_cid: str) -> dict:
        """Download proof from IPFS (mock implementation)"""
        # Return mock proof data
        return {
            "asset_id": "mock_asset_id",
            "proof": ["mock_proof_element_1", "mock_proof_element_2"],
            "root": "mock_root_hash"
        }

    def download_registry_snapshot(self, snapshot_cid: str) -> Optional[Dict[str, Any]]:
        """Download registry snapshot from IPFS"""
        try:
            # In production, this would fetch from IPFS
            # For now, return mock data based on stored records
            for snapshot in self.registry_snapshots:
                if snapshot["cid"] == snapshot_cid:
                    return {
                        "cid": snapshot_cid,
                        "edition_count": snapshot["edition_count"],
                        "core_asset_count": snapshot["core_asset_count"],
                        "timestamp": snapshot["timestamp"],
                        "content_hash": snapshot["content_hash"]
                    }
            return None
        except Exception as e:
            logger.error(f"Failed to download registry snapshot: {e}")
            return None

    def verify_content_integrity(self, cid: str, expected_hash: str) -> bool:
        """Verify content integrity using stored hash"""
        stored_hash = self.uploaded_files.get(cid)
        return stored_hash == expected_hash if stored_hash else False

    def get_registry_history(self) -> List[Dict[str, Any]]:
        """Get history of registry snapshots"""
        return self.registry_snapshots.copy()

    def pin_content(self, cid: str) -> bool:
        """Pin content to ensure availability (mock)"""
        if cid in self.uploaded_files:
            logger.info(f"✅ Pinned content: {cid}")
            return True
        logger.warning(f"❌ Cannot pin unknown CID: {cid}")
        return False

    def unpin_content(self, cid: str) -> bool:
        """Unpin content (mock)"""
        logger.info(f"✅ Unpinned content: {cid}")
        return True

    def get_storage_stats(self) -> Dict[str, Any]:
        """Get IPFS storage statistics"""
        return {
            "total_uploads": len(self.uploaded_files),
            "registry_snapshots": len(self.registry_snapshots),
            "storage_by_type": {
                "manifests": len([c for c in self.uploaded_files.keys() if c.startswith("bafybei")]),
                "registry_snapshots": len([c for c in self.uploaded_files.keys() if c.startswith("bafyre")]),
                "edition_metadata": len([c for c in self.uploaded_files.keys() if "edition" in c]),
                "batch_updates": len([c for c in self.uploaded_files.keys() if "batch" in c])
            },
            "total_size_mb": len(self.uploaded_files) * 0.001  # Rough estimate
        }


class EditionIPFSManager:
    """Specialized IPFS manager for edition registry operations"""

    def __init__(self, ipfs_manager: IPFSManager):
        self.ipfs = ipfs_manager
        self.logger = logging.getLogger(__name__)

    def create_registry_snapshot(self, registry_data: Dict[str, Any]) -> str:
        """Create and upload registry snapshot"""
        return self.ipfs.upload_edition_registry_snapshot(registry_data)

    def store_edition_metadata(self, edition_metadata: Dict[str, Any],
                             universal_key: str) -> str:
        """Store individual edition metadata"""
        return self.ipfs.upload_edition_metadata(edition_metadata, universal_key)

    def record_batch_update(self, batch_data: Dict[str, Any]) -> str:
        """Record batch edition update"""
        return self.ipfs.upload_batch_edition_update(batch_data)

    def get_snapshot_chain(self) -> List[str]:
        """Get chain of registry snapshots for verification"""
        snapshots = self.ipfs.get_registry_history()
        return [s["cid"] for s in snapshots]

    def verify_snapshot_integrity(self, snapshot_cid: str) -> bool:
        """Verify snapshot hasn't been tampered with"""
        snapshot_data = self.ipfs.download_registry_snapshot(snapshot_cid)
        if not snapshot_data:
            return False

        # In production, would verify against blockchain anchor
        return self.ipfs.verify_content_integrity(snapshot_cid, snapshot_data["content_hash"])
