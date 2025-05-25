import os
import hashlib
import base64
import json
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from storage_manager import StorageManager

class AuthManager:
    """Manages user authentication and master password handling."""
    
    def __init__(self, storage_manager: StorageManager):
        self.storage_manager = storage_manager
        
    def derive_key(self, password: str, salt: bytes = None):
        """
        Derive a cryptographic key from the master password.
        
        Args:
            password: The master password string
            salt: Optional salt bytes, generated if not provided
            
        Returns:
            tuple: (key, salt) where key is the derived key and salt is the salt used
        """
        if salt is None:
            salt = os.urandom(16)
            
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key, salt
    
    def hash_password(self, password: str, salt: bytes = None):
        """
        Hash the master password for storage.
        
        Args:
            password: The master password to hash
            salt: Optional salt bytes, generated if not provided
            
        Returns:
            tuple: (hash_hex, salt_hex) where both are hex encoded strings
        """
        if salt is None:
            salt = os.urandom(16)
            
        # Combine password with salt and hash
        salted_password = password.encode() + salt
        hash_obj = hashlib.sha256(salted_password)
        password_hash = hash_obj.hexdigest()
        
        return password_hash, salt.hex()
    
    def verify_password(self, entered_password: str, stored_hash: str, stored_salt: str):
        """
        Verify an entered password against the stored hash.
        
        Args:
            entered_password: The password entered by user
            stored_hash: The stored password hash
            stored_salt: The stored salt (hex encoded)
            
        Returns:
            bool: True if password matches, False otherwise
        """
        salt = bytes.fromhex(stored_salt)
        salted_password = entered_password.encode() + salt
        hash_obj = hashlib.sha256(salted_password)
        computed_hash = hash_obj.hexdigest()
        
        return computed_hash == stored_hash
    
    def is_first_run(self):
        """Check if this is the first run of the application."""
        return not self.storage_manager.master_config_exists()
    
    def create_master_password(self, password: str):
        """
        Create a new master password.
        
        Args:
            password: The master password to set
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Hash password for storage
        password_hash, salt_hex = self.hash_password(password)
        
        # Derive encryption key
        key, key_salt = self.derive_key(password)
        
        # Store master configuration
        master_config = {
            "password_hash": password_hash,
            "password_salt": salt_hex,
            "key_salt": key_salt.hex()
        }
        
        return self.storage_manager.save_master_config(master_config)
    
    def verify_master_password(self, password: str):
        """
        Verify the master password.
        
        Args:
            password: The password to verify
            
        Returns:
            tuple: (is_valid, key) where is_valid is a boolean and key is the derived key if valid
        """
        try:
            # Load master configuration
            master_config = self.storage_manager.load_master_config()
            
            # Verify the password
            is_valid = self.verify_password(
                password,
                master_config["password_hash"],
                master_config["password_salt"]
            )
            
            if is_valid:
                # Derive the key using stored salt
                key_salt = bytes.fromhex(master_config["key_salt"])
                key, _ = self.derive_key(password, key_salt)
                return True, key
            
            return False, None
        
        except Exception as e:
            print(f"Error verifying master password: {e}")
            return False, None
