import customtkinter as ctk
import time
from datetime import datetime

class SharedPasswordsFrame(ctk.CTkFrame):
    """Frame for viewing and managing shared passwords."""
    
    def __init__(self, parent, sharing_manager):
        super().__init__(parent)
        self.parent = parent
        self.sharing_manager = sharing_manager
        
        # Create UI elements
        self.create_widgets()
        
        # Load shared passwords
        self.load_shared_passwords()
    
    def create_widgets(self):
        """Create all widgets for the shared passwords frame."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Shared Passwords",
            font=("Roboto", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="View and manage passwords you have shared with others",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 20))
        
        # Create button frame
        self.button_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        self.refresh_button = ctk.CTkButton(
            self.button_frame,
            text="Refresh",
            width=100,
            command=self.load_shared_passwords
        )
        self.refresh_button.pack(side="left")
        
        self.access_shared_button = ctk.CTkButton(
            self.button_frame,
            text="Access Shared Password",
            width=180,
            command=self.show_access_shared_dialog
        )
        self.access_shared_button.pack(side="right")
        
        # Create list container frame
        self.list_container = ctk.CTkFrame(self)
        self.list_container.grid(row=3, column=0, sticky="nsew", padx=20, pady=(0, 20))
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame for shared password entries
        self.scrollable_frame = ctk.CTkScrollableFrame(self.list_container)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        
        # Empty state label
        self.empty_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="No passwords have been shared yet.",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        
        # Configure grid row weights
        self.grid_rowconfigure(3, weight=1)
        
        # Notification area
        self.notification_frame = ctk.CTkFrame(self)
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=("Roboto", 12)
        )
        self.notification_label.pack(pady=5)
    
    def load_shared_passwords(self):
        """Load and display shared passwords."""
        # Clear current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        # Get active shares
        shared_items = self.sharing_manager.get_active_shares()
        
        if not shared_items:
            # Show empty state
            self.empty_label.pack(pady=50)
        else:
            # Display shared items
            for i, item in enumerate(shared_items):
                self.create_shared_item_widget(item, i)
    
    def create_shared_item_widget(self, item, index):
        """Create a widget for a shared password item."""
        # Get share information
        share_id = item.get("id", "")
        created_at = item.get("created_at", 0)
        expires_at = item.get("expires_at", 0)
        access_count = item.get("access_count_current", 0)
        access_limit = item.get("access_count_limit", 1)
        
        # Format timestamps
        created_date = datetime.fromtimestamp(created_at).strftime("%Y-%m-%d %H:%M")
        expires_date = datetime.fromtimestamp(expires_at).strftime("%Y-%m-%d %H:%M")
        
        # Calculate remaining time
        now = time.time()
        remaining_seconds = max(0, expires_at - now)
        remaining_hours = remaining_seconds / 3600
        
        if remaining_hours < 1:
            remaining_text = f"{int(remaining_seconds / 60)} minutes remaining"
        elif remaining_hours < 24:
            remaining_text = f"{int(remaining_hours)} hours remaining"
        elif remaining_hours < 48:
            remaining_text = f"1 day remaining"
        else:
            remaining_text = f"{int(remaining_hours / 24)} days remaining"
        
        # Create item frame
        item_frame = ctk.CTkFrame(self.scrollable_frame)
        item_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Configure grid
        item_frame.grid_columnconfigure(0, weight=1)
        
        # Share ID (truncated)
        id_text = f"Share ID: {share_id[:8]}..."
        id_label = ctk.CTkLabel(
            item_frame,
            text=id_text,
            font=("Roboto", 12, "bold")
        )
        id_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        
        # Created and expiry dates
        dates_label = ctk.CTkLabel(
            item_frame,
            text=f"Created: {created_date} • Expires: {expires_date}",
            font=("Roboto", 11),
            text_color=("gray40", "gray60")
        )
        dates_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))
        
        # Status frame
        status_frame = ctk.CTkFrame(item_frame, fg_color=("gray90", "gray20"))
        status_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        # Remaining time
        remaining_label = ctk.CTkLabel(
            status_frame,
            text=remaining_text,
            font=("Roboto", 11),
            text_color=("#2563EB", "#3B82F6")
        )
        remaining_label.pack(side="left", padx=10, pady=5)
        
        # Access count
        if access_limit > 0:
            access_text = f"Accessed {access_count}/{access_limit} times"
        else:
            access_text = f"Accessed {access_count} times"
            
        access_label = ctk.CTkLabel(
            status_frame,
            text=access_text,
            font=("Roboto", 11)
        )
        access_label.pack(side="right", padx=10, pady=5)
        
        # Revoke button
        revoke_button = ctk.CTkButton(
            item_frame,
            text="Revoke Access",
            width=120,
            fg_color="#E11D48",
            hover_color="#9F1239",
            command=lambda sid=share_id: self.revoke_access(sid)
        )
        revoke_button.grid(row=3, column=0, sticky="e", padx=10, pady=(0, 10))
    
    def revoke_access(self, share_id):
        """Revoke access to a shared password."""
        success = self.sharing_manager.invalidate_shared_item(share_id)
        
        if success:
            self.show_notification(f"Access to shared password has been revoked")
            self.load_shared_passwords()
        else:
            self.show_notification("Failed to revoke access")
    
    def show_access_shared_dialog(self):
        """Show dialog for accessing a shared password."""
        from ui.access_shared_dialog import AccessSharedDialog
        dialog = AccessSharedDialog(self.parent, self.sharing_manager)
    
    def show_notification(self, message):
        """Show a temporary notification message."""
        self.notification_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.notification_label.configure(text=message)
        
        # Hide after 3 seconds
        self.after(3000, self.hide_notification)
    
    def hide_notification(self):
        """Hide the notification."""
        self.notification_frame.grid_forget()