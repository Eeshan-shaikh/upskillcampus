import customtkinter as ctk
import tkinter as tk
import pyperclip
import threading
import time

class ShareDialog(ctk.CTkToplevel):
    """Dialog for sharing a password entry with time-limited access."""
    
    def __init__(self, parent, sharing_manager, entry):
        super().__init__(parent)
        self.parent = parent
        self.sharing_manager = sharing_manager
        self.entry = entry
        
        # Configure window
        self.title("Share Password")
        self.geometry("500x480")
        self.transient(parent)  # Set to be on top of the main window
        self.grab_set()  # Make window modal
        
        # Create UI elements
        self.create_widgets()
        
        # Center the dialog
        self.after(10, self.center_window)
    
    def center_window(self):
        """Center the dialog on the parent window."""
        self.update_idletasks()
        parent_x = self.parent.winfo_rootx()
        parent_y = self.parent.winfo_rooty()
        parent_width = self.parent.winfo_width()
        parent_height = self.parent.winfo_height()
        
        width = self.winfo_width()
        height = self.winfo_height()
        
        x = parent_x + (parent_width // 2) - (width // 2)
        y = parent_y + (parent_height // 2) - (height // 2)
        
        self.geometry(f"+{x}+{y}")
    
    def create_widgets(self):
        """Create all widgets for the sharing dialog."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title and description
        self.title_label = ctk.CTkLabel(
            self,
            text="Share Password Securely",
            font=("Roboto", 18, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self,
            text=f"Share '{self.entry.get('title', 'Untitled')}' with time-limited access",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 20))
        
        # Options frame
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Expiration options
        self.expiration_label = ctk.CTkLabel(
            self.options_frame,
            text="Link Expires After:",
            font=("Roboto", 12, "bold")
        )
        self.expiration_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.expiration_values = ["1 hour", "6 hours", "12 hours", "24 hours", "3 days", "7 days"]
        self.expiration_hours = [1, 6, 12, 24, 72, 168]
        
        self.expiration_var = ctk.StringVar(value="24 hours")
        self.expiration_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=self.expiration_values,
            variable=self.expiration_var
        )
        self.expiration_menu.grid(row=0, column=1, sticky="w", padx=15, pady=(15, 5))
        
        # Access count options
        self.access_label = ctk.CTkLabel(
            self.options_frame,
            text="Maximum Number of Accesses:",
            font=("Roboto", 12, "bold")
        )
        self.access_label.grid(row=1, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.access_values = ["1 time", "2 times", "3 times", "5 times", "10 times", "Unlimited"]
        self.access_counts = [1, 2, 3, 5, 10, 0]  # 0 means unlimited
        
        self.access_var = ctk.StringVar(value="1 time")
        self.access_menu = ctk.CTkOptionMenu(
            self.options_frame,
            values=self.access_values,
            variable=self.access_var
        )
        self.access_menu.grid(row=1, column=1, sticky="w", padx=15, pady=(15, 5))
        
        # Warning message
        self.warning_frame = ctk.CTkFrame(self, fg_color=("light yellow", "#5A4000"))
        self.warning_frame.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        self.warning_label = ctk.CTkLabel(
            self.warning_frame,
            text="⚠️ Warning: Shared passwords may be viewed by anyone with the link.\n"
                 "Ensure you're sharing with trusted recipients only.",
            font=("Roboto", 12),
            text_color=("black", "white")
        )
        self.warning_label.pack(padx=15, pady=10)
        
        # Share button
        self.share_button = ctk.CTkButton(
            self,
            text="Generate Sharing Link",
            font=("Roboto", 14),
            height=40,
            command=self.generate_sharing_link
        )
        self.share_button.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Result frame (initially hidden)
        self.result_frame = ctk.CTkFrame(self)
        
        self.result_label = ctk.CTkLabel(
            self.result_frame,
            text="Share this link and access key with the recipient:",
            font=("Roboto", 12, "bold")
        )
        self.result_label.pack(anchor="w", padx=15, pady=(15, 5))
        
        # Link frame
        self.link_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.link_frame.pack(fill="x", padx=15, pady=5)
        
        self.link_label = ctk.CTkLabel(
            self.link_frame,
            text="Link:",
            font=("Roboto", 12),
            width=50
        )
        self.link_label.pack(side="left")
        
        self.link_entry = ctk.CTkEntry(
            self.link_frame,
            font=("Roboto", 12)
        )
        self.link_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        self.copy_link_button = ctk.CTkButton(
            self.link_frame,
            text="Copy",
            width=60,
            command=self.copy_link
        )
        self.copy_link_button.pack(side="right")
        
        # Access key frame
        self.key_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.key_frame.pack(fill="x", padx=15, pady=5)
        
        self.key_label = ctk.CTkLabel(
            self.key_frame,
            text="Key:",
            font=("Roboto", 12),
            width=50
        )
        self.key_label.pack(side="left")
        
        self.key_entry = ctk.CTkEntry(
            self.key_frame,
            font=("Roboto", 12),
            show="•"
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(5, 5))
        
        self.show_key_var = ctk.BooleanVar(value=False)
        self.show_key_cb = ctk.CTkCheckBox(
            self.key_frame,
            text="Show",
            variable=self.show_key_var,
            command=self.toggle_key_visibility,
            width=60
        )
        self.show_key_cb.pack(side="right")
        
        self.copy_key_button = ctk.CTkButton(
            self.key_frame,
            text="Copy",
            width=60,
            command=self.copy_key
        )
        self.copy_key_button.pack(side="right", padx=(0, 5))
        
        # Expiration info
        self.expiry_info_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        self.expiry_info_label.pack(anchor="w", padx=15, pady=(10, 5))
        
        # Access info
        self.access_info_label = ctk.CTkLabel(
            self.result_frame,
            text="",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        self.access_info_label.pack(anchor="w", padx=15, pady=(0, 10))
        
        # Information on how to use
        self.usage_label = ctk.CTkLabel(
            self.result_frame,
            text="🔹 The recipient will need both the link and the access key to view the password.\n"
                 "🔹 For better security, send the link and key through different channels.",
            font=("Roboto", 12),
            justify="left"
        )
        self.usage_label.pack(anchor="w", padx=15, pady=(5, 15))
        
        # Close button in result view
        self.close_button = ctk.CTkButton(
            self.result_frame,
            text="Close",
            font=("Roboto", 14),
            height=40,
            command=self.destroy
        )
        self.close_button.pack(fill="x", padx=15, pady=(0, 15))
        
        # Notification area
        self.notification_frame = ctk.CTkFrame(self)
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=("Roboto", 12)
        )
        self.notification_label.pack(pady=5)
        
        # Cancel button
        self.cancel_button = ctk.CTkButton(
            self,
            text="Cancel",
            font=("Roboto", 14),
            height=40,
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self.destroy
        )
        self.cancel_button.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
    
    def generate_sharing_link(self):
        """Generate a sharing link and display it."""
        # Get selected expiration time
        expiration_index = self.expiration_values.index(self.expiration_var.get())
        expiration_hours = self.expiration_hours[expiration_index]
        
        # Get selected access count
        access_index = self.access_values.index(self.access_var.get())
        access_count = self.access_counts[access_index]
        
        # Create sharing link
        share_id, access_key = self.sharing_manager.create_sharing_link(
            self.entry, 
            expiration_hours=expiration_hours,
            access_count=access_count
        )
        
        if not share_id or not access_key:
            self.show_notification("Failed to create sharing link")
            return
        
        # Create sharing URL (this would be a real URL in production)
        base_url = "https://securepass.example.com/shared/"
        share_url = f"{base_url}{share_id}"
        
        # Display the result
        self.link_entry.delete(0, tk.END)
        self.link_entry.insert(0, share_url)
        
        self.key_entry.delete(0, tk.END)
        self.key_entry.insert(0, access_key)
        
        # Set expiry info
        if expiration_hours == 1:
            expiry_text = "Expires in 1 hour"
        elif expiration_hours < 24:
            expiry_text = f"Expires in {expiration_hours} hours"
        elif expiration_hours == 24:
            expiry_text = "Expires in 1 day"
        elif expiration_hours == 72:
            expiry_text = "Expires in 3 days"
        elif expiration_hours == 168:
            expiry_text = "Expires in 7 days"
        else:
            expiry_text = f"Expires in {expiration_hours} hours"
            
        self.expiry_info_label.configure(text=expiry_text)
        
        # Set access info
        if access_count == 0:
            access_text = "Can be accessed unlimited times"
        elif access_count == 1:
            access_text = "Can be accessed 1 time only"
        else:
            access_text = f"Can be accessed up to {access_count} times"
            
        self.access_info_label.configure(text=access_text)
        
        # Hide options and show result
        self.options_frame.grid_forget()
        self.warning_frame.grid_forget()
        self.share_button.grid_forget()
        self.cancel_button.grid_forget()
        
        self.result_frame.grid(row=3, column=0, rowspan=3, sticky="nsew", padx=20, pady=(0, 20))
    
    def toggle_key_visibility(self):
        """Toggle access key visibility."""
        current_key = self.key_entry.get()
        show_char = "" if self.show_key_var.get() else "•"
        
        self.key_entry.delete(0, tk.END)
        self.key_entry.configure(show=show_char)
        self.key_entry.insert(0, current_key)
    
    def copy_link(self):
        """Copy the sharing link to clipboard."""
        link = self.link_entry.get()
        if link:
            pyperclip.copy(link)
            self.show_notification("Link copied to clipboard!")
    
    def copy_key(self):
        """Copy the access key to clipboard."""
        key = self.key_entry.get()
        if key:
            pyperclip.copy(key)
            self.show_notification("Access key copied to clipboard!")
            
            # Auto-clear clipboard after 30 seconds for security
            threading.Timer(30, self.clear_clipboard, args=[key]).start()
    
    def clear_clipboard(self, expected_value):
        """Clear clipboard if it still contains the sensitive data."""
        current_clipboard = pyperclip.paste()
        if current_clipboard == expected_value:
            pyperclip.copy("")
    
    def show_notification(self, message):
        """Show a temporary notification message."""
        self.notification_frame.grid(row=6, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.notification_label.configure(text=message)
        
        # Hide after 3 seconds
        self.after(3000, self.hide_notification)
    
    def hide_notification(self):
        """Hide the notification."""
        self.notification_frame.grid_forget()