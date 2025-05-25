import customtkinter as ctk
import os
import threading
import time
from datetime import datetime

class SettingsFrame(ctk.CTkFrame):
    """Frame for application settings and utilities."""
    
    def __init__(self, parent, theme_manager, storage_manager):
        super().__init__(parent)
        self.parent = parent
        self.theme_manager = theme_manager
        self.storage_manager = storage_manager
        
        # Get current settings
        self.settings = self.storage_manager.get_app_settings()
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the settings frame."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Settings",
            font=("Roboto", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 30))
        
        # Settings sections
        self.create_appearance_section()
        self.create_security_section()
        self.create_backup_section()
        self.create_about_section()
        
        # Save button
        self.save_button = ctk.CTkButton(
            self,
            text="Save Settings",
            font=("Roboto", 14),
            command=self.save_settings
        )
        self.save_button.grid(row=5, column=0, sticky="ew", padx=20, pady=(20, 20))
        
        # Notification area
        self.notification_frame = ctk.CTkFrame(self)
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=("Roboto", 12)
        )
        self.notification_label.pack(pady=5)
    
    def create_appearance_section(self):
        """Create appearance settings section."""
        self.appearance_frame = ctk.CTkFrame(self)
        self.appearance_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Section title
        self.appearance_label = ctk.CTkLabel(
            self.appearance_frame,
            text="Appearance",
            font=("Roboto", 14, "bold")
        )
        self.appearance_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Theme options
        self.theme_frame = ctk.CTkFrame(self.appearance_frame, fg_color="transparent")
        self.theme_frame.pack(fill="x", padx=15, pady=5)
        
        self.theme_label = ctk.CTkLabel(
            self.theme_frame,
            text="Theme Mode:",
            font=("Roboto", 12)
        )
        self.theme_label.pack(side="left", padx=(0, 10))
        
        self.theme_var = ctk.StringVar(value=self.settings.get("theme_mode", "system"))
        self.theme_menu = ctk.CTkOptionMenu(
            self.theme_frame,
            values=["Light", "Dark", "System"],
            variable=self.theme_var,
            command=self.change_theme
        )
        self.theme_menu.pack(side="left")
    
    def create_security_section(self):
        """Create security settings section."""
        self.security_frame = ctk.CTkFrame(self)
        self.security_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Section title
        self.security_label = ctk.CTkLabel(
            self.security_frame,
            text="Security",
            font=("Roboto", 14, "bold")
        )
        self.security_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Clipboard timeout
        self.clipboard_frame = ctk.CTkFrame(self.security_frame, fg_color="transparent")
        self.clipboard_frame.pack(fill="x", padx=15, pady=5)
        
        self.clipboard_label = ctk.CTkLabel(
            self.clipboard_frame,
            text="Clear clipboard after:",
            font=("Roboto", 12)
        )
        self.clipboard_label.pack(side="left", padx=(0, 10))
        
        self.clipboard_var = ctk.StringVar(value=self.settings.get("clipboard_timeout", "30 seconds"))
        self.clipboard_menu = ctk.CTkOptionMenu(
            self.clipboard_frame,
            values=["10 seconds", "30 seconds", "1 minute", "5 minutes", "Never"],
            variable=self.clipboard_var
        )
        self.clipboard_menu.pack(side="left")
        
        # Auto logout
        self.logout_frame = ctk.CTkFrame(self.security_frame, fg_color="transparent")
        self.logout_frame.pack(fill="x", padx=15, pady=5)
        
        self.logout_label = ctk.CTkLabel(
            self.logout_frame,
            text="Auto logout after:",
            font=("Roboto", 12)
        )
        self.logout_label.pack(side="left", padx=(0, 10))
        
        self.logout_var = ctk.StringVar(value=self.settings.get("auto_logout", "Never"))
        self.logout_menu = ctk.CTkOptionMenu(
            self.logout_frame,
            values=["5 minutes", "15 minutes", "30 minutes", "1 hour", "Never"],
            variable=self.logout_var
        )
        self.logout_menu.pack(side="left")
    
    def create_backup_section(self):
        """Create backup and restore section."""
        self.backup_frame = ctk.CTkFrame(self)
        self.backup_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Section title
        self.backup_label = ctk.CTkLabel(
            self.backup_frame,
            text="Backup & Restore",
            font=("Roboto", 14, "bold")
        )
        self.backup_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Description
        self.backup_desc = ctk.CTkLabel(
            self.backup_frame,
            text="Create backups of your password database for safekeeping.",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        self.backup_desc.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Backup button
        self.backup_button = ctk.CTkButton(
            self.backup_frame,
            text="Create Backup",
            command=self.create_backup
        )
        self.backup_button.pack(anchor="w", padx=15, pady=(0, 10))
    
    def create_about_section(self):
        """Create about section."""
        self.about_frame = ctk.CTkFrame(self)
        self.about_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Section title
        self.about_label = ctk.CTkLabel(
            self.about_frame,
            text="About",
            font=("Roboto", 14, "bold")
        )
        self.about_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # App info
        self.app_name = ctk.CTkLabel(
            self.about_frame,
            text="SecurePass Manager",
            font=("Roboto", 12, "bold")
        )
        self.app_name.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.app_version = ctk.CTkLabel(
            self.about_frame,
            text="Version 1.0.0",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        self.app_version.pack(anchor="w", padx=15, pady=(0, 5))
        
        self.app_desc = ctk.CTkLabel(
            self.about_frame,
            text="A secure, modern password manager built with Python.",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        self.app_desc.pack(anchor="w", padx=15, pady=(0, 10))
    
    def change_theme(self, theme_name):
        """Change the application theme."""
        theme_name = theme_name.lower()
        self.theme_manager.set_theme_mode(theme_name)
    
    def create_backup(self):
        """Create a backup of the password database."""
        success = self.storage_manager.backup_passwords()
        
        if success:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.show_notification(f"Backup created successfully at {timestamp}")
        else:
            self.show_notification("Failed to create backup. No password data exists yet.")
    
    def save_settings(self):
        """Save all settings."""
        # Collect settings from UI
        settings = {
            "theme_mode": self.theme_var.get().lower(),
            "clipboard_timeout": self.clipboard_var.get(),
            "auto_logout": self.logout_var.get()
        }
        
        # Save to storage
        if self.storage_manager.save_app_settings(settings):
            self.show_notification("Settings saved successfully!")
            self.settings = settings
        else:
            self.show_notification("Failed to save settings")
    
    def show_notification(self, message):
        """Show a temporary notification message."""
        self.notification_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.notification_label.configure(text=message)
        
        # Hide after 3 seconds
        self.after(3000, self.hide_notification)
    
    def hide_notification(self):
        """Hide the notification."""
        self.notification_frame.grid_forget()
