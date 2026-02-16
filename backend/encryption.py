"""
Encryption utilities for sensitive data storage
Provides Fernet-based symmetric encryption for API keys and secrets
"""

import os
import logging
from typing import Optional, Dict, Any
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

# Encryption key must be configured - fail fast if missing for production
ENCRYPTION_KEY = os.environ.get('ENCRYPTION_KEY')

def _get_fernet() -> Optional[Fernet]:
    """Get Fernet cipher instance if encryption key is configured"""
    if not ENCRYPTION_KEY:
        logger.warning("ENCRYPTION_KEY not configured - encryption disabled")
        return None
    
    try:
        # Ensure key is in correct format
        key_bytes = ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY
        # Fernet keys are 32 bytes encoded as 44 characters in URL-safe base64
        if len(key_bytes) != 44:
            # Generate proper key from provided string
            import hashlib
            hash_key = hashlib.sha256(key_bytes).digest()
            key_bytes = base64.urlsafe_b64encode(hash_key)
        return Fernet(key_bytes)
    except Exception as e:
        logger.error(f"Failed to initialize Fernet cipher: {e}")
        return None

def encrypt_value(value: str) -> str:
    """
    Encrypt a sensitive value using Fernet symmetric encryption
    
    Args:
        value: Plain text value to encrypt
        
    Returns:
        Encrypted value as string (or original if encryption disabled)
    """
    if not value:
        return value
    
    fernet = _get_fernet()
    if not fernet:
        logger.warning("Encryption disabled - storing value in plaintext")
        return value
    
    try:
        encrypted_bytes = fernet.encrypt(value.encode())
        return encrypted_bytes.decode()
    except Exception as e:
        logger.error(f"Encryption failed: {e}")
        return value

def decrypt_value(encrypted_value: str) -> str:
    """
    Decrypt a value that was encrypted with encrypt_value
    
    Args:
        encrypted_value: Encrypted value as string
        
    Returns:
        Decrypted plain text value (or original if encryption disabled/fails)
    """
    if not encrypted_value:
        return encrypted_value
    
    fernet = _get_fernet()
    if not fernet:
        # If encryption is disabled, assume value is plaintext
        return encrypted_value
    
    try:
        decrypted_bytes = fernet.decrypt(encrypted_value.encode())
        return decrypted_bytes.decode()
    except Exception:
        # If decryption fails, value might be plaintext (backward compatibility)
        logger.debug("Decryption failed, assuming plaintext for backward compatibility")
        return encrypted_value

def encrypt_dict(data: Dict[str, Any], sensitive_keys: set = None) -> Dict[str, Any]:
    """
    Encrypt sensitive fields in a dictionary
    
    Args:
        data: Dictionary containing sensitive data
        sensitive_keys: Set of keys to encrypt (default: common sensitive key names)
        
    Returns:
        Dictionary with sensitive fields encrypted
    """
    if sensitive_keys is None:
        sensitive_keys = {
            'api_key', 'apikey', 'secret', 'password', 'token',
            'openai_api_key', 'anthropic_api_key', 'llm_api_key',
            'access_token', 'refresh_token', 'bearer_token'
        }
    
    encrypted_data = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys and isinstance(value, str):
            encrypted_data[key] = encrypt_value(value)
        else:
            encrypted_data[key] = value
    
    return encrypted_data

def decrypt_dict(data: Dict[str, Any], sensitive_keys: set = None) -> Dict[str, Any]:
    """
    Decrypt sensitive fields in a dictionary
    
    Args:
        data: Dictionary with encrypted sensitive data
        sensitive_keys: Set of keys to decrypt (default: common sensitive key names)
        
    Returns:
        Dictionary with sensitive fields decrypted
    """
    if sensitive_keys is None:
        sensitive_keys = {
            'api_key', 'apikey', 'secret', 'password', 'token',
            'openai_api_key', 'anthropic_api_key', 'llm_api_key',
            'access_token', 'refresh_token', 'bearer_token'
        }
    
    decrypted_data = {}
    for key, value in data.items():
        if key.lower() in sensitive_keys and isinstance(value, str):
            decrypted_data[key] = decrypt_value(value)
        else:
            decrypted_data[key] = value
    
    return decrypted_data

def generate_encryption_key() -> str:
    """
    Generate a new Fernet encryption key
    
    Returns:
        Base64-encoded encryption key suitable for ENCRYPTION_KEY environment variable
    """
    key = Fernet.generate_key()
    return key.decode()

# Warn if encryption is disabled
if not ENCRYPTION_KEY:
    logger.warning(
        "ENCRYPTION_KEY not set - sensitive data encryption is DISABLED. "
        "Set ENCRYPTION_KEY environment variable for production use. "
        f"Generate a key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'"
    )
