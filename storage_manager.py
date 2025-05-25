import os
import json
import base64
from pathlib import Path
from datetime import datetime

class StorageManager:
    """Manages data storage for the password manager."""
    
    def __init__(self):
        """Initialize the storage manager with paths."""
        # Define storage directory
        self.data_dir = os.path.join(str(Path.home()), ".securepass")
        self.config_file = os.path.join(self.data_dir, "config.json")
        self.passwords_file = os.path.join(self.data_dir, "passwords.dat")
        
        # Ensure directory exists
        self._ensure_data_dir_exists()
    
    def _ensure_data_dir_exists(self):
        """Create the data directory if it doesn't exist."""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
    def master_config_exists(self):
        """Check if the master configuration file exists."""
        return os.path.exists(self.config_file)
    
    def save_master_config(self, config_data):
        """
        Save master configuration data.
        
        Args:
            config_data: Dictionary containing configuration data
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config_data, f)
            return True
        except Exception as e:
            print(f"Error saving master configuration: {e}")
            return False
    
    def load_master_config(self):
        """
        Load master configuration data.
        
        Returns:
            dict: Configuration data
        """
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading master configuration: {e}")
            return None
    
    def save_encrypted_passwords(self, encrypted_data):
        """
        Save encrypted password data.
        
        Args:
            encrypted_data: Encrypted bytes
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            with open(self.passwords_file, 'wb') as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"Error saving encrypted passwords: {e}")
            return False
    
    def load_encrypted_passwords(self):
        """
        Load encrypted password data.
        
        Returns:
            bytes: Encrypted data or None if file doesn't exist
        """
        if not os.path.exists(self.passwords_file):
            return None
            
        try:
            with open(self.passwords_file, 'rb') as f:
                return f.read()
        except Exception as e:
            print(f"Error loading encrypted passwords: {e}")
            return None
    
    def backup_passwords(self):
        """
        Create a backup of the passwords file.
        
        Returns:
            bool: True if successful, False otherwise
        """
        if not os.path.exists(self.passwords_file):
            return False
            
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = os.path.join(self.data_dir, f"passwords_backup_{timestamp}.dat")
            
            with open(self.passwords_file, 'rb') as source:
                with open(backup_file, 'wb') as target:
                    target.write(source.read())
            return True
        except Exception as e:
            print(f"Error creating backup: {e}")
            return False
            
    def get_app_settings(self):
        """
        Get application settings.
        
        Returns:
            dict: Application settings
        """
        try:
            config = self.load_master_config()
            if config and "app_settings" in config:
                return config["app_settings"]
            return {"theme_mode": "system"}
        except Exception as e:
            print(f"Error loading app settings: {e}")
            return {"theme_mode": "system"}
    
    def save_app_settings(self, settings):
        """
        Save application settings.
        
        Args:
            settings: Dictionary containing application settings
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            config = self.load_master_config()
            if config:
                config["app_settings"] = settings
                return self.save_master_config(config)
            return False
        except Exception as e:
            print(f"Error saving app settings: {e}")
            return False
