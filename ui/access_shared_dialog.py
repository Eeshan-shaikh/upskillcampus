import customtkinter as ctk
import tkinter as tk
import pyperclip
import threading
import time
import re
import webbrowser

class AccessSharedDialog(ctk.CTkToplevel):
    """Dialog for accessing a shared password entry."""
    
    def __init__(self, parent, sharing_manager):
        super().__init__(parent)
        self.parent = parent
        self.sharing_manager = sharing_manager
        
        # Configure window
        self.title("Access Shared Password")
        self.geometry("500x400")
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
        """Create all widgets for the access dialog."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title and description
        self.title_label = ctk.CTkLabel(
            self,
            text="Access Shared Password",
            font=("Roboto", 18, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 5))
        
        self.subtitle_label = ctk.CTkLabel(
            self,
            text="Enter the sharing link and access key to view the shared password",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        self.subtitle_label.grid(row=1, column=0, sticky="w", padx=20, pady=(0, 20))
        
        # Input frame
        self.input_frame = ctk.CTkFrame(self)
        self.input_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Link input
        self.link_label = ctk.CTkLabel(
            self.input_frame,
            text="Sharing Link:",
            font=("Roboto", 12, "bold")
        )
        self.link_label.grid(row=0, column=0, sticky="w", padx=15, pady=(15, 5))
        
        self.link_entry = ctk.CTkEntry(
            self.input_frame,
            placeholder_text="https://securepass.example.com/shared/...",
            width=400
        )
        self.link_entry.grid(row=1, column=0, sticky="ew", padx=15, pady=(0, 15))
        
        # Access key input
        self.key_label = ctk.CTkLabel(
            self.input_frame,
            text="Access Key:",
            font=("Roboto", 12, "bold")
        )
        self.key_label.grid(row=2, column=0, sticky="w", padx=15, pady=(0, 5))
        
        self.key_frame = ctk.CTkFrame(self.input_frame, fg_color="transparent")
        self.key_frame.grid(row=3, column=0, sticky="ew", padx=15, pady=(0, 15))
        self.key_frame.grid_columnconfigure(0, weight=1)
        
        self.key_entry = ctk.CTkEntry(
            self.key_frame,
            placeholder_text="Enter the access key provided by the sender",
            show="•"
        )
        self.key_entry.grid(row=0, column=0, sticky="ew")
        
        self.show_key_var = ctk.BooleanVar(value=False)
        self.show_key_cb = ctk.CTkCheckBox(
            self.key_frame,
            text="Show key",
            variable=self.show_key_var,
            command=self.toggle_key_visibility
        )
        self.show_key_cb.grid(row=0, column=1, padx=(10, 0))
        
        # Access button
        self.access_button = ctk.CTkButton(
            self,
            text="Access Password",
            font=("Roboto", 14),
            height=40,
            command=self.access_shared_password
        )
        self.access_button.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 10))
        
        # Result frame (initially hidden)
        self.result_frame = ctk.CTkFrame(self)
        
        # Displayed password details
        self.password_title_label = ctk.CTkLabel(
            self.result_frame,
            text="Password Details:",
            font=("Roboto", 14, "bold")
        )
        self.password_title_label.pack(anchor="w", padx=15, pady=(15, 10))
        
        # Service/title
        self.service_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.service_frame.pack(fill="x", padx=15, pady=(0, 5))
        
        self.service_label = ctk.CTkLabel(
            self.service_frame,
            text="Service:",
            font=("Roboto", 12, "bold"),
            width=80
        )
        self.service_label.pack(side="left")
        
        self.service_value = ctk.CTkLabel(
            self.service_frame,
            text="",
            font=("Roboto", 12)
        )
        self.service_value.pack(side="left", fill="x", expand=True)
        
        # Username
        self.username_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.username_frame.pack(fill="x", padx=15, pady=5)
        
        self.username_label = ctk.CTkLabel(
            self.username_frame,
            text="Username:",
            font=("Roboto", 12, "bold"),
            width=80
        )
        self.username_label.pack(side="left")
        
        self.username_value = ctk.CTkLabel(
            self.username_frame,
            text="",
            font=("Roboto", 12)
        )
        self.username_value.pack(side="left", fill="x", expand=True)
        
        self.copy_username_button = ctk.CTkButton(
            self.username_frame,
            text="Copy",
            width=60,
            command=self.copy_username
        )
        self.copy_username_button.pack(side="right")
        
        # Password
        self.password_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.password_frame.pack(fill="x", padx=15, pady=5)
        
        self.password_label = ctk.CTkLabel(
            self.password_frame,
            text="Password:",
            font=("Roboto", 12, "bold"),
            width=80
        )
        self.password_label.pack(side="left")
        
        self.password_entry = ctk.CTkEntry(
            self.password_frame,
            font=("Roboto", 12),
            show="•"
        )
        self.password_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_cb = ctk.CTkCheckBox(
            self.password_frame,
            text="Show",
            variable=self.show_password_var,
            command=self.toggle_password_visibility,
            width=60
        )
        self.show_password_cb.pack(side="right")
        
        self.copy_password_button = ctk.CTkButton(
            self.password_frame,
            text="Copy",
            width=60,
            command=self.copy_password
        )
        self.copy_password_button.pack(side="right", padx=(0, 5))
        
        # Website
        self.website_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.website_frame.pack(fill="x", padx=15, pady=5)
        
        self.website_label = ctk.CTkLabel(
            self.website_frame,
            text="Website:",
            font=("Roboto", 12, "bold"),
            width=80
        )
        self.website_label.pack(side="left")
        
        self.website_value = ctk.CTkLabel(
            self.website_frame,
            text="",
            font=("Roboto", 12)
        )
        self.website_value.pack(side="left", fill="x", expand=True)
        
        self.visit_button = ctk.CTkButton(
            self.website_frame,
            text="Visit",
            width=60,
            command=self.visit_website
        )
        
        # Notes (if any)
        self.notes_frame = ctk.CTkFrame(self.result_frame, fg_color="transparent")
        self.notes_frame.pack(fill="x", padx=15, pady=5)
        
        self.notes_label = ctk.CTkLabel(
            self.notes_frame,
            text="Notes:",
            font=("Roboto", 12, "bold"),
            width=80,
            anchor="nw"
        )
        self.notes_label.pack(side="left", anchor="n")
        
        self.notes_text = ctk.CTkTextbox(
            self.notes_frame,
            font=("Roboto", 12),
            height=80,
            activate_scrollbars=True
        )
        self.notes_text.pack(side="left", fill="both", expand=True, padx=(0, 0))
        self.notes_text.configure(state="disabled")
        
        # Close button
        self.close_result_button = ctk.CTkButton(
            self.result_frame,
            text="Close",
            font=("Roboto", 14),
            height=40,
            command=self.destroy
        )
        self.close_result_button.pack(fill="x", padx=15, pady=(15, 15))
        
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
        self.cancel_button.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Notification area
        self.notification_frame = ctk.CTkFrame(self)
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=("Roboto", 12)
        )
        self.notification_label.pack(pady=5)
    
    def toggle_key_visibility(self):
        """Toggle access key visibility."""
        current_key = self.key_entry.get()
        show_char = "" if self.show_key_var.get() else "•"
        
        self.key_entry.delete(0, tk.END)
        self.key_entry.configure(show=show_char)
        self.key_entry.insert(0, current_key)
    
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        current_password = self.password_entry.get()
        show_char = "" if self.show_password_var.get() else "•"
        
        self.password_entry.delete(0, tk.END)
        self.password_entry.configure(show=show_char)
        self.password_entry.insert(0, current_password)
    
    def access_shared_password(self):
        """Access the shared password using the provided link and key."""
        # Get link and key
        link = self.link_entry.get().strip()
        key = self.key_entry.get().strip()
        
        if not link or not key:
            self.show_notification("Please enter both the sharing link and access key")
            return
        
        # Extract the share ID from the link
        share_id = self.extract_share_id(link)
        if not share_id:
            self.show_notification("Invalid sharing link format")
            return
        
        # Access the shared item
        entry = self.sharing_manager.access_shared_item(share_id, key)
        if not entry:
            self.show_notification("Invalid link or access key, or the shared item has expired")
            return
        
        # Display the shared password details
        self.display_shared_entry(entry)
    
    def extract_share_id(self, link):
        """Extract the share ID from a sharing link."""
        # Example link format: https://securepass.example.com/shared/1234-5678-90ab-cdef
        pattern = r'shared/([a-zA-Z0-9-]+)'
        match = re.search(pattern, link)
        
        if match:
            return match.group(1)
        return None
    
    def display_shared_entry(self, entry):
        """Display the shared password entry details."""
        # Set values
        self.service_value.configure(text=entry.get("title", "Untitled"))
        self.username_value.configure(text=entry.get("username", ""))
        
        # Set password
        self.password_entry.delete(0, tk.END)
        self.password_entry.insert(0, entry.get("password", ""))
        
        # Set website
        website = entry.get("website", "")
        self.website_value.configure(text=website)
        
        # Show/hide visit button based on whether there's a website
        if website and (website.startswith("http://") or website.startswith("https://")):
            self.visit_button.pack(side="right")
        else:
            self.visit_button.pack_forget()
        
        # Set notes
        notes = entry.get("notes", "")
        self.notes_text.configure(state="normal")
        self.notes_text.delete("1.0", tk.END)
        if notes:
            self.notes_text.insert("1.0", notes)
        self.notes_text.configure(state="disabled")
        
        # Hide input frame and show result frame
        self.input_frame.grid_forget()
        self.access_button.grid_forget()
        self.cancel_button.grid_forget()
        
        self.result_frame.grid(row=2, column=0, rowspan=3, sticky="nsew", padx=20, pady=(0, 20))
    
    def copy_username(self):
        """Copy the username to clipboard."""
        username = self.username_value.cget("text")
        if username:
            pyperclip.copy(username)
            self.show_notification("Username copied to clipboard!")
    
    def copy_password(self):
        """Copy the password to clipboard."""
        password = self.password_entry.get()
        if password:
            pyperclip.copy(password)
            self.show_notification("Password copied to clipboard!")
            
            # Auto-clear clipboard after 30 seconds for security
            threading.Timer(30, self.clear_clipboard, args=[password]).start()
    
    def visit_website(self):
        """Open the website in the default browser."""
        website = self.website_value.cget("text")
        if website:
            try:
                webbrowser.open(website)
            except Exception as e:
                self.show_notification(f"Failed to open website: {e}")
    
    def clear_clipboard(self, expected_value):
        """Clear clipboard if it still contains the sensitive data."""
        current_clipboard = pyperclip.paste()
        if current_clipboard == expected_value:
            pyperclip.copy("")
    
    def show_notification(self, message):
        """Show a temporary notification message."""
        self.notification_frame.grid(row=5, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.notification_label.configure(text=message)
        
        # Hide after 3 seconds
        self.after(3000, self.hide_notification)
    
    def hide_notification(self):
        """Hide the notification."""
        self.notification_frame.grid_forget()