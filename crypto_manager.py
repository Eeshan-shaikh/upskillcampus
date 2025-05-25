import base64
import json
from cryptography.fernet import Fernet

class CryptoManager:
    """Manages encryption and decryption of sensitive data."""
    
    def __init__(self, key):
        """
        Initialize the crypto manager with a key.
        
        Args:
            key: Base64 encoded key for Fernet encryption
        """
        self.fernet = Fernet(key)
        
    def encrypt_data(self, data):
        """
        Encrypt data (dictionary).
        
        Args:
            data: Dictionary containing data to encrypt
            
        Returns:
            bytes: Encrypted data
        """
        # Convert dictionary to JSON string
        json_data = json.dumps(data)
        # Encrypt the data
        encrypted_data = self.fernet.encrypt(json_data.encode())
        return encrypted_data
    
    def decrypt_data(self, encrypted_data):
        """
        Decrypt data.
        
        Args:
            encrypted_data: Encrypted data bytes
            
        Returns:
            dict: Decrypted data as dictionary
        """
        try:
            # Decrypt the data
            decrypted_data = self.fernet.decrypt(encrypted_data)
            # Convert JSON string back to dictionary
            json_data = json.loads(decrypted_data.decode())
            return json_data
        except Exception as e:
            print(f"Error decrypting data: {e}")
            return None
    
    def encrypt_password(self, password):
        """
        Encrypt a single password string.
        
        Args:
            password: Password string to encrypt
            
        Returns:
            str: Base64 encoded encrypted password
        """
        encrypted = self.fernet.encrypt(password.encode())
        return base64.b64encode(encrypted).decode()
    
    def decrypt_password(self, encrypted_password):
        """
        Decrypt a single password string.
        
        Args:
            encrypted_password: Base64 encoded encrypted password
            
        Returns:
            str: Decrypted password
        """
        try:
            encrypted = base64.b64decode(encrypted_password)
            decrypted = self.fernet.decrypt(encrypted)
            return decrypted.decode()
        except Exception as e:
            print(f"Error decrypting password: {e}")
            return None
