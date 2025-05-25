import customtkinter as ctk
from datetime import datetime
import pyperclip
import tkinter as tk
import time
import threading
import random
import string

class PasswordEntryFrame(ctk.CTkFrame):
    """Frame for viewing, editing, or creating a password entry."""
    
    def __init__(self, parent, crypto_manager, entry=None, on_save=None, on_delete=None, categories=None, password_generator=None):
        super().__init__(parent)
        self.parent = parent
        self.crypto_manager = crypto_manager
        self.entry = entry or {}  # Use empty dict for new entries
        self.on_save = on_save
        self.on_delete = on_delete
        self.categories = categories or ["All"]
        self.password_generator = password_generator
        
        # Track if this is a new entry
        self.is_new = entry is None
        
        # UI elements
        self.show_password = False
        
        # Build UI
        self.create_widgets()
        self.load_entry_data()
    
    def create_widgets(self):
        """Create all UI widgets for the entry form."""
        # Configure grid for main layout
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        title_text = "Add New Password" if self.is_new else "Edit Password"
        self.title_label = ctk.CTkLabel(
            self,
            text=title_text,
            font=("Roboto", 18, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 20))
        
        # Form fields in a scrollable frame
        self.form_container = ctk.CTkScrollableFrame(
            self,
            label_text="Password Details"
        )
        self.form_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 10))
        self.grid_rowconfigure(1, weight=1)
        
        # Form grid configuration
        self.form_container.grid_columnconfigure(0, weight=0)
        self.form_container.grid_columnconfigure(1, weight=1)
        
        # Title field
        self.title_field_label = ctk.CTkLabel(
            self.form_container,
            text="Title:",
            font=("Roboto", 12, "bold")
        )
        self.title_field_label.grid(row=0, column=0, sticky="w", padx=(0, 10), pady=(10, 5))
        
        self.title_field = ctk.CTkEntry(
            self.form_container,
            placeholder_text="e.g. Google Account"
        )
        self.title_field.grid(row=0, column=1, sticky="ew", pady=(10, 5))
        
        # Website field
        self.website_label = ctk.CTkLabel(
            self.form_container,
            text="Website:",
            font=("Roboto", 12, "bold")
        )
        self.website_label.grid(row=1, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.website_field = ctk.CTkEntry(
            self.form_container,
            placeholder_text="e.g. https://google.com"
        )
        self.website_field.grid(row=1, column=1, sticky="ew", pady=5)
        
        # Username field
        self.username_label = ctk.CTkLabel(
            self.form_container,
            text="Username:",
            font=("Roboto", 12, "bold")
        )
        self.username_label.grid(row=2, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.username_field = ctk.CTkEntry(
            self.form_container,
            placeholder_text="e.g. user@example.com"
        )
        self.username_field.grid(row=2, column=1, sticky="ew", pady=5)
        
        # Password field with additional controls
        self.password_label = ctk.CTkLabel(
            self.form_container,
            text="Password:",
            font=("Roboto", 12, "bold")
        )
        self.password_label.grid(row=3, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.password_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.password_frame.grid(row=3, column=1, sticky="ew", pady=5)
        self.password_frame.grid_columnconfigure(0, weight=1)
        
        self.password_field = ctk.CTkEntry(
            self.password_frame,
            placeholder_text="Enter password",
            show="•"
        )
        self.password_field.grid(row=0, column=0, sticky="ew")
        
        self.password_buttons_frame = ctk.CTkFrame(self.password_frame, fg_color="transparent")
        self.password_buttons_frame.grid(row=1, column=0, sticky="e", pady=(5, 0))
        
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_cb = ctk.CTkCheckBox(
            self.password_buttons_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        self.show_password_cb.pack(side="left", padx=(0, 10))
        
        self.generate_button = ctk.CTkButton(
            self.password_buttons_frame,
            text="Generate",
            width=80,
            command=self.generate_password
        )
        self.generate_button.pack(side="left", padx=(0, 10))
        
        self.copy_button = ctk.CTkButton(
            self.password_buttons_frame,
            text="Copy",
            width=80,
            command=self.copy_password
        )
        self.copy_button.pack(side="left")
        
        # Category field with option to add new
        self.category_label = ctk.CTkLabel(
            self.form_container,
            text="Category:",
            font=("Roboto", 12, "bold")
        )
        self.category_label.grid(row=4, column=0, sticky="w", padx=(0, 10), pady=5)
        
        self.category_frame = ctk.CTkFrame(self.form_container, fg_color="transparent")
        self.category_frame.grid(row=4, column=1, sticky="ew", pady=5)
        self.category_frame.grid_columnconfigure(0, weight=1)
        
        # Filter out "All" from categories
        dropdown_categories = [cat for cat in self.categories if cat != "All"]
        
        self.category_var = ctk.StringVar(value="")
        self.category_dropdown = ctk.CTkComboBox(
            self.category_frame,
            values=dropdown_categories,
            variable=self.category_var
        )
        self.category_dropdown.grid(row=0, column=0, sticky="ew")
        
        # Notes field
        self.notes_label = ctk.CTkLabel(
            self.form_container,
            text="Notes:",
            font=("Roboto", 12, "bold")
        )
        self.notes_label.grid(row=5, column=0, sticky="nw", padx=(0, 10), pady=5)
        
        self.notes_field = ctk.CTkTextbox(
            self.form_container,
            height=100
        )
        self.notes_field.grid(row=5, column=1, sticky="ew", pady=5)
        
        # Metadata section for timestamps (only for existing entries)
        if not self.is_new:
            self.metadata_frame = ctk.CTkFrame(self.form_container)
            self.metadata_frame.grid(row=6, column=0, columnspan=2, sticky="ew", pady=(20, 5))
            
            self.metadata_label = ctk.CTkLabel(
                self.metadata_frame,
                text="Metadata",
                font=("Roboto", 12, "bold")
            )
            self.metadata_label.pack(anchor="w", padx=10, pady=(5, 0))
            
            # Creation time
            created_time = self.entry.get("created_at", "Unknown")
            if isinstance(created_time, int) or isinstance(created_time, float):
                created_time = datetime.fromtimestamp(created_time).strftime("%Y-%m-%d %H:%M:%S")
                
            self.created_label = ctk.CTkLabel(
                self.metadata_frame,
                text=f"Created: {created_time}",
                font=("Roboto", 11),
                text_color=("gray40", "gray60")
            )
            self.created_label.pack(anchor="w", padx=10, pady=(0, 5))
            
            # Last modified time
            modified_time = self.entry.get("modified_at", "Unknown")
            if isinstance(modified_time, int) or isinstance(modified_time, float):
                modified_time = datetime.fromtimestamp(modified_time).strftime("%Y-%m-%d %H:%M:%S")
                
            self.modified_label = ctk.CTkLabel(
                self.metadata_frame,
                text=f"Last modified: {modified_time}",
                font=("Roboto", 11),
                text_color=("gray40", "gray60")
            )
            self.modified_label.pack(anchor="w", padx=10, pady=(0, 5))
        
        # Button row
        self.button_frame = ctk.CTkFrame(self)
        self.button_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        if not self.is_new and self.on_delete:
            self.delete_button = ctk.CTkButton(
                self.button_frame,
                text="Delete",
                fg_color="#e74c3c",
                hover_color="#c0392b",
                command=self.handle_delete
            )
            self.delete_button.pack(side="left", padx=(0, 10))
        
        self.cancel_button = ctk.CTkButton(
            self.button_frame,
            text="Cancel",
            fg_color="transparent",
            border_width=1,
            text_color=("gray10", "gray90"),
            command=self.handle_cancel
        )
        self.cancel_button.pack(side="left", padx=(0, 10))
        
        self.save_button = ctk.CTkButton(
            self.button_frame,
            text="Save",
            command=self.handle_save
        )
        self.save_button.pack(side="right")
        
        # Notification area for copy confirmation
        self.notification_frame = ctk.CTkFrame(self)
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=("Roboto", 12)
        )
        self.notification_label.pack(pady=5)
    
    def load_entry_data(self):
        """Load entry data into form fields."""
        if self.is_new:
            # Set current timestamps for new entries
            self.entry["created_at"] = time.time()
            self.entry["modified_at"] = time.time()
            return
            
        # Load data for existing entry
        self.title_field.insert(0, self.entry.get("title", ""))
        self.website_field.insert(0, self.entry.get("website", ""))
        self.username_field.insert(0, self.entry.get("username", ""))
        
        # Decrypt password if encrypted
        password = self.entry.get("password", "")
        if password and "encrypted" in self.entry and self.entry["encrypted"]:
            try:
                password = self.crypto_manager.decrypt_password(password)
            except Exception as e:
                print(f"Error decrypting password: {e}")
                password = ""
        
        self.password_field.insert(0, password)
        
        # Set category
        category = self.entry.get("category", "")
        if category:
            self.category_var.set(category)
        
        # Set notes
        notes = self.entry.get("notes", "")
        if notes:
            self.notes_field.insert("1.0", notes)
    
    def toggle_password_visibility(self):
        """Toggle password field visibility."""
        self.show_password = self.show_password_var.get()
        current_password = self.password_field.get()
        show_char = "" if self.show_password else "•"
        
        # Need to clear and reinsert to change show character
        self.password_field.delete(0, tk.END)
        self.password_field.configure(show=show_char)
        self.password_field.insert(0, current_password)
    
    def generate_password(self):
        """Generate a secure password."""
        if self.password_generator:
            password = self.password_generator.generate_password(
                length=16,
                include_uppercase=True,
                include_lowercase=True,
                include_numbers=True,
                include_symbols=True
            )
            
            # Clear current password and insert new one
            self.password_field.delete(0, tk.END)
            self.password_field.insert(0, password)
            
            # Show notification
            self.show_notification("Password generated!")
    
    def copy_password(self):
        """Copy password to clipboard."""
        password = self.password_field.get()
        if password:
            pyperclip.copy(password)
            self.show_notification("Password copied to clipboard!")
            
            # Auto-clear clipboard after 30 seconds
            threading.Timer(30, self.clear_clipboard, args=[password]).start()
    
    def clear_clipboard(self, expected_value):
        """Clear clipboard if it still contains the password."""
        current_clipboard = pyperclip.paste()
        if current_clipboard == expected_value:
            pyperclip.copy("")
    
    def show_notification(self, message):
        """Show a temporary notification message."""
        self.notification_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.notification_label.configure(text=message)
        
        # Hide after 3 seconds
        self.after(3000, self.hide_notification)
    
    def hide_notification(self):
        """Hide the notification."""
        self.notification_frame.grid_forget()
    
    def handle_save(self):
        """Handle save button click."""
        # Validate required fields
        if not self.validate_form():
            return
            
        # Update entry data
        title = self.title_field.get()
        website = self.website_field.get()
        username = self.username_field.get()
        password = self.password_field.get()
        category = self.category_var.get()
        notes = self.notes_field.get("1.0", tk.END).strip()
        
        # Create new entry object (not modifying the original)
        new_entry = dict(self.entry)
        new_entry["title"] = title
        new_entry["website"] = website
        new_entry["username"] = username
        
        # Encrypt password
        new_entry["password"] = self.crypto_manager.encrypt_password(password)
        new_entry["encrypted"] = True
        
        new_entry["category"] = category
        new_entry["notes"] = notes
        
        # Update timestamps
        if self.is_new:
            new_entry["created_at"] = time.time()
        new_entry["modified_at"] = time.time()
        
        # Call the appropriate callback
        if self.is_new:
            if self.on_save:
                self.on_save(new_entry)
        else:
            if self.on_save:
                self.on_save(self.entry, new_entry)
                
        # Close the dialog
        self.parent.destroy()
    
    def validate_form(self):
        """Validate form fields before saving."""
        # Title is required
        if not self.title_field.get():
            self.show_notification("Title is required!")
            self.title_field.focus_set()
            return False
            
        # Password is required
        if not self.password_field.get():
            self.show_notification("Password is required!")
            self.password_field.focus_set()
            return False
            
        return True
    
    def handle_cancel(self):
        """Handle cancel button click."""
        self.parent.destroy()
    
    def handle_delete(self):
        """Handle delete button click."""
        # Confirm deletion
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("300x150")
        dialog.transient(self.parent)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.parent.winfo_rootx() + (self.parent.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.parent.winfo_rooty() + (self.parent.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            dialog,
            text="Are you sure you want to delete this password?\nThis action cannot be undone.",
            font=("Roboto", 12)
        )
        label.pack(pady=(20, 10))
        
        button_frame = ctk.CTkFrame(dialog, fg_color="transparent")
        button_frame.pack(fill="x", padx=10, pady=10)
        
        cancel_button = ctk.CTkButton(
            button_frame,
            text="Cancel",
            width=100,
            command=dialog.destroy
        )
        cancel_button.pack(side="left", padx=10)
        
        confirm_button = ctk.CTkButton(
            button_frame,
            text="Delete",
            width=100,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=lambda: self.confirm_delete(dialog)
        )
        confirm_button.pack(side="right", padx=10)
    
    def confirm_delete(self, dialog):
        """Confirm and process deletion."""
        dialog.destroy()
        
        if self.on_delete:
            self.on_delete(self.entry)
            
        self.parent.destroy()
