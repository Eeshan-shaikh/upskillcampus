import os
import base64
import json
import time
import uuid
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

class SharingManager:
    """Manages secure password sharing with time-limited access."""
    
    def __init__(self, storage_manager, crypto_manager):
        """
        Initialize the sharing manager.
        
        Args:
            storage_manager: StorageManager instance for storing shared items
            crypto_manager: CryptoManager instance for encryption/decryption
        """
        self.storage_manager = storage_manager
        self.crypto_manager = crypto_manager
        
        # Ensure shared items directory exists
        self.shared_dir = os.path.join(self.storage_manager.data_dir, "shared")
        if not os.path.exists(self.shared_dir):
            os.makedirs(self.shared_dir)
    
    def create_sharing_link(self, entry, expiration_hours=24, access_count=1):
        """
        Create a secure sharing link for a password entry.
        
        Args:
            entry: The password entry to share
            expiration_hours: Number of hours until the link expires
            access_count: Maximum number of times the link can be accessed
            
        Returns:
            tuple: (share_id, access_key) where share_id identifies the shared item
                  and access_key is required to decrypt it
        """
        # Generate a random access key for this share
        access_key = base64.urlsafe_b64encode(os.urandom(32)).decode()
        
        # Decrypt the password if it's encrypted
        password = entry.get("password", "")
        if password and entry.get("encrypted", False):
            try:
                password = self.crypto_manager.decrypt_password(password)
            except Exception as e:
                print(f"Error decrypting password for sharing: {e}")
                return None, None
        
        # Create a copy of the entry for sharing
        shared_entry = {
            "title": entry.get("title", ""),
            "username": entry.get("username", ""),
            "password": password,
            "website": entry.get("website", ""),
            "notes": entry.get("notes", ""),
            "category": entry.get("category", "")
        }
        
        # Generate a unique ID for this shared item
        share_id = str(uuid.uuid4())
        
        # Set up expiration details
        expiration_time = time.time() + (expiration_hours * 3600)
        
        # Encrypt the entry with the access key
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'sharing_salt',  # Fixed salt for simplicity
            iterations=100000,
        )
        sharing_key = base64.urlsafe_b64encode(kdf.derive(access_key.encode()))
        fernet = Fernet(sharing_key)
        
        encrypted_data = fernet.encrypt(json.dumps(shared_entry).encode())
        
        # Create share metadata
        share_data = {
            "encrypted_entry": base64.b64encode(encrypted_data).decode(),
            "created_at": time.time(),
            "expires_at": expiration_time,
            "access_count_limit": access_count,
            "access_count_current": 0,
            "is_valid": True
        }
        
        # Save shared item
        self._save_shared_item(share_id, share_data)
        
        return share_id, access_key
    
    def access_shared_item(self, share_id, access_key):
        """
        Access a shared password item.
        
        Args:
            share_id: ID of the shared item
            access_key: Key required to decrypt the shared item
            
        Returns:
            dict: The shared password entry or None if invalid/expired
        """
        # Load the shared item
        share_data = self._load_shared_item(share_id)
        if not share_data:
            return None
        
        # Check if share is valid
        if not share_data.get("is_valid", False):
            return None
        
        # Check if expired
        current_time = time.time()
        if current_time > share_data.get("expires_at", 0):
            # Mark as invalid due to expiration
            share_data["is_valid"] = False
            self._save_shared_item(share_id, share_data)
            return None
        
        # Check access count
        current_count = share_data.get("access_count_current", 0)
        limit = share_data.get("access_count_limit", 1)
        
        if limit > 0 and current_count >= limit:
            # Mark as invalid due to max access count reached
            share_data["is_valid"] = False
            self._save_shared_item(share_id, share_data)
            return None
        
        # Increment access count
        share_data["access_count_current"] = current_count + 1
        if limit > 0 and share_data["access_count_current"] >= limit:
            share_data["is_valid"] = False
        
        # Save updated access count
        self._save_shared_item(share_id, share_data)
        
        # Decrypt the shared item
        try:
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'sharing_salt',  # Fixed salt for simplicity
                iterations=100000,
            )
            sharing_key = base64.urlsafe_b64encode(kdf.derive(access_key.encode()))
            fernet = Fernet(sharing_key)
            
            encrypted_data = base64.b64decode(share_data["encrypted_entry"])
            decrypted_data = fernet.decrypt(encrypted_data)
            
            return json.loads(decrypted_data.decode())
        except Exception as e:
            print(f"Error decrypting shared item: {e}")
            return None
    
    def invalidate_shared_item(self, share_id):
        """
        Invalidate a shared item so it can no longer be accessed.
        
        Args:
            share_id: ID of the shared item to invalidate
            
        Returns:
            bool: True if successful, False otherwise
        """
        share_data = self._load_shared_item(share_id)
        if not share_data:
            return False
        
        share_data["is_valid"] = False
        return self._save_shared_item(share_id, share_data)
    
    def get_active_shares(self):
        """
        Get a list of all active shares created by the user.
        
        Returns:
            list: List of share metadata dictionaries
        """
        shares = []
        
        if not os.path.exists(self.shared_dir):
            return shares
        
        for filename in os.listdir(self.shared_dir):
            if filename.endswith(".json"):
                share_id = filename[:-5]  # Remove .json extension
                share_data = self._load_shared_item(share_id)
                
                if share_data and share_data.get("is_valid", False):
                    # Check if expired
                    if time.time() > share_data.get("expires_at", 0):
                        share_data["is_valid"] = False
                        self._save_shared_item(share_id, share_data)
                        continue
                    
                    # Add share ID to the data
                    share_info = {
                        "id": share_id,
                        "created_at": share_data.get("created_at"),
                        "expires_at": share_data.get("expires_at"),
                        "access_count_limit": share_data.get("access_count_limit"),
                        "access_count_current": share_data.get("access_count_current"),
                        "is_valid": share_data.get("is_valid")
                    }
                    shares.append(share_info)
        
        return shares
    
    def _save_shared_item(self, share_id, share_data):
        """
        Save a shared item to storage.
        
        Args:
            share_id: ID of the shared item
            share_data: Dictionary containing share metadata and encrypted entry
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            file_path = os.path.join(self.shared_dir, f"{share_id}.json")
            with open(file_path, 'w') as f:
                json.dump(share_data, f)
            return True
        except Exception as e:
            print(f"Error saving shared item: {e}")
            return False
    
    def _load_shared_item(self, share_id):
        """
        Load a shared item from storage.
        
        Args:
            share_id: ID of the shared item
            
        Returns:
            dict: Share data or None if not found
        """
        file_path = os.path.join(self.shared_dir, f"{share_id}.json")
        
        if not os.path.exists(file_path):
            return None
        
        try:
            with open(file_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading shared item: {e}")
            return None