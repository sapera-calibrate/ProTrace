"""
ProTrace EIP-712 Signing Module
===============================

EIP-712 typed signature generation and verification for gasless registrations.
Includes nonce management and replay protection.
"""

from typing import Dict, Tuple
import json
import hashlib
import time


# EIP-712 Domain Separator
DOMAIN = {
    "name": "ProTrace UniquenessGuardian",
    "version": "2.0",
    "chainId": 1,  # Ethereum mainnet (update for other chains)
    "verifyingContract": "0x0000000000000000000000000000000000000000"  # Set after deployment
}

# EIP-712 Type Definitions
TYPES = {
    "EIP712Domain": [
        {"name": "name", "type": "string"},
        {"name": "version", "type": "string"},
        {"name": "chainId", "type": "uint256"},
        {"name": "verifyingContract", "type": "address"}
    ],
    "Registration": [
        {"name": "dna_bits", "type": "bytes32"},
        {"name": "pointer", "type": "string"},
        {"name": "nonce", "type": "uint256"},
        {"name": "tokenId", "type": "uint256"},
        {"name": "platformId", "type": "string"},
        {"name": "deadline", "type": "uint256"}
    ]
}


class NonceManager:
    """
    Manage nonces for replay protection.
    Each platform address has an incremental nonce.
    """
    
    def __init__(self):
        self.nonces = {}
    
    def get_nonce(self, address: str) -> int:
        """Get current nonce for address"""
        address = address.lower()
        return self.nonces.get(address, 0)
    
    def increment_nonce(self, address: str) -> int:
        """Increment and return new nonce"""
        address = address.lower()
        current = self.nonces.get(address, 0)
        self.nonces[address] = current + 1
        return self.nonces[address]
    
    def set_nonce(self, address: str, nonce: int):
        """Set nonce for address (e.g., sync with on-chain)"""
        address = address.lower()
        self.nonces[address] = nonce


# Global nonce manager instance
nonce_manager = NonceManager()


def build_registration_message(
    dna_hex: str,
    pointer: str,
    token_id: int,
    platform_id: str,
    signer_address: str,
    deadline: int = None
) -> Dict:
    """
    Build EIP-712 registration message.
    
    Args:
        dna_hex: 128-bit DNA as 32-char hex
        pointer: Unique identifier
        token_id: Token ID
        platform_id: Platform identifier
        signer_address: Platform wallet address
        deadline: Unix timestamp (default: 1 hour from now)
    
    Returns:
        Message dictionary ready for signing
    """
    if deadline is None:
        deadline = int(time.time()) + 3600  # 1 hour validity
    
    # Get current nonce for platform
    nonce = nonce_manager.get_nonce(signer_address)
    
    # Convert DNA hex to bytes32 format (with 0x prefix)
    if not dna_hex.startswith('0x'):
        dna_hex = '0x' + dna_hex
    
    # Pad to 32 bytes if needed
    if len(dna_hex) < 66:  # 0x + 64 hex chars
        dna_hex = dna_hex + '0' * (66 - len(dna_hex))
    
    message = {
        "dna_bits": dna_hex,
        "pointer": pointer,
        "nonce": nonce,
        "tokenId": token_id,
        "platformId": platform_id,
        "deadline": deadline
    }
    
    return message


def verify_signature_offline(message: Dict, signature: str, expected_signer: str) -> bool:
    """
    Verify EIP-712 signature off-chain (requires eth_account).
    
    Args:
        message: Registration message
        signature: Signature string (hex with 0x prefix)
        expected_signer: Expected signer address
    
    Returns:
        True if signature is valid
    """
    try:
        from eth_account.messages import encode_structured_data
        from eth_account import Account
        
        # Build structured data
        structured_data = {
            "types": TYPES,
            "primaryType": "Registration",
            "domain": DOMAIN,
            "message": message
        }
        
        # Encode
        encoded_message = encode_structured_data(structured_data)
        
        # Recover signer
        recovered_address = Account.recover_message(
            encoded_message,
            signature=signature
        )
        
        # Compare addresses (case-insensitive)
        return recovered_address.lower() == expected_signer.lower()
        
    except ImportError:
        print("⚠️  eth-account not installed. Install with: pip install eth-account")
        return False
    except Exception as e:
        print(f"❌ Signature verification failed: {e}")
        return False


def sign_message(message: Dict, private_key: str) -> str:
    """
    Sign EIP-712 message with private key.
    
    Args:
        message: Registration message
        private_key: Private key (hex string with or without 0x)
    
    Returns:
        Signature string (hex with 0x prefix)
    """
    try:
        from eth_account.messages import encode_structured_data
        from eth_account import Account
        
        # Remove 0x prefix if present
        if private_key.startswith('0x'):
            private_key = private_key[2:]
        
        # Build structured data
        structured_data = {
            "types": TYPES,
            "primaryType": "Registration",
            "domain": DOMAIN,
            "message": message
        }
        
        # Encode
        encoded_message = encode_structured_data(structured_data)
        
        # Sign
        account = Account.from_key(private_key)
        signed_message = account.sign_message(encoded_message)
        
        return signed_message.signature.hex()
        
    except ImportError:
        print("⚠️  eth-account not installed. Install with: pip install eth-account")
        return None
    except Exception as e:
        print(f"❌ Signing failed: {e}")
        return None


def parse_signature(signature: str) -> Tuple[int, str, str]:
    """
    Parse signature into v, r, s components.
    
    Args:
        signature: Signature hex string
    
    Returns:
        Tuple of (v, r, s) as (int, hex_string, hex_string)
    """
    # Remove 0x prefix
    if signature.startswith('0x'):
        signature = signature[2:]
    
    # Extract components
    r = '0x' + signature[0:64]
    s = '0x' + signature[64:128]
    v = int(signature[128:130], 16)
    
    return (v, r, s)


def format_for_contract(message: Dict, signature: str) -> Dict:
    """
    Format message and signature for smart contract call.
    
    Args:
        message: Registration message
        signature: Signature hex string
    
    Returns:
        Dictionary with contract-ready parameters
    """
    v, r, s = parse_signature(signature)
    
    return {
        "dna_bits": message["dna_bits"],
        "pointer": message["pointer"],
        "tokenId": message["tokenId"],
        "platformId": message["platformId"],
        "deadline": message["deadline"],
        "v": v,
        "r": r,
        "s": s
    }


def update_domain(chain_id: int, contract_address: str):
    """
    Update domain separator with deployed contract address.
    
    Args:
        chain_id: Blockchain chain ID (1 = Ethereum, 137 = Polygon, etc.)
        contract_address: Deployed GuardianOracle contract address
    """
    global DOMAIN
    DOMAIN["chainId"] = chain_id
    DOMAIN["verifyingContract"] = contract_address
    print(f"✅ Updated EIP-712 domain: Chain {chain_id}, Contract {contract_address}")


def get_domain_info() -> Dict:
    """Get current domain configuration"""
    return DOMAIN.copy()


def get_types_info() -> Dict:
    """Get EIP-712 type definitions"""
    return TYPES.copy()


# Example usage for testing
if __name__ == "__main__":
    # Example: Build and sign message
    test_message = build_registration_message(
        dna_hex="abc123def456" + "0" * 20,
        pointer="uuid:550e8400-opensea-ethereum",
        token_id=42,
        platform_id="opensea",
        signer_address="0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb",
        deadline=int(time.time()) + 3600
    )
    
    print("Message to sign:")
    print(json.dumps(test_message, indent=2))
    
    # Note: In production, signing happens on client side (MetaMask, etc.)
    # This is just for testing
    
    # Format for contract
    # contract_params = format_for_contract(test_message, signature)
    # print("\nContract parameters:")
    # print(json.dumps(contract_params, indent=2))
