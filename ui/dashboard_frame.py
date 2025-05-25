import customtkinter as ctk
from typing import List, Dict, Any
from ui.password_entry_frame import PasswordEntryFrame
from ui.generator_frame import GeneratorFrame
from ui.settings_frame import SettingsFrame
from ui.shared_passwords_frame import SharedPasswordsFrame
from ui.share_dialog import ShareDialog
from ui.access_shared_dialog import AccessSharedDialog
from password_generator import PasswordGenerator
from sharing_manager import SharingManager

class DashboardFrame(ctk.CTkFrame):
    """Main dashboard frame containing password list and management functions."""
    
    def __init__(self, parent, crypto_manager, storage_manager, theme_manager, on_logout):
        super().__init__(parent)
        self.parent = parent
        self.crypto_manager = crypto_manager
        self.storage_manager = storage_manager
        self.theme_manager = theme_manager
        self.on_logout = on_logout
        self.password_generator = PasswordGenerator()
        self.sharing_manager = SharingManager(storage_manager, crypto_manager)
        
        # Data storage
        self.password_entries = []
        self.selected_category = "All"
        self.categories = ["All"]
        self.search_text = ""
        
        # UI setup
        self.create_widgets()
        
        # Load data
        self.load_passwords()
        
    def create_widgets(self):
        """Create and arrange all dashboard widgets."""
        # Create main layout with two columns
        self.grid_columnconfigure(0, weight=0)  # Sidebar
        self.grid_columnconfigure(1, weight=1)  # Content
        self.grid_rowconfigure(0, weight=1)
        
        # Create sidebar
        self.create_sidebar()
        
        # Create main content area
        self.content_frame = ctk.CTkFrame(self)
        self.content_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)
        
        # Configure content frame grid
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_rowconfigure(0, weight=0)  # Header
        self.content_frame.grid_rowconfigure(1, weight=1)  # Password list
        
        # Create header
        self.create_header()
        
        # Create password list area with scrollable frame
        self.create_password_list()
        
        # Create floating action button for adding new passwords
        self.create_add_button()
        
        # Start with passwords tab selected
        self.show_passwords_list()
    
    def create_sidebar(self):
        """Create the sidebar with navigation buttons."""
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew", padx=(10, 0), pady=10)
        self.sidebar.grid_propagate(False)
        
        # App title
        self.title_label = ctk.CTkLabel(
            self.sidebar, 
            text="SecurePass",
            font=("Roboto", 20, "bold")
        )
        self.title_label.pack(pady=(20, 30))
        
        # Navigation buttons
        self.nav_buttons_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.nav_buttons_frame.pack(fill="x", padx=10)
        
        # Passwords button
        self.passwords_button = ctk.CTkButton(
            self.nav_buttons_frame,
            text="Passwords",
            command=self.show_passwords_list,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w"
        )
        self.passwords_button.pack(fill="x", pady=(0, 5))
        
        # Generator button
        self.generator_button = ctk.CTkButton(
            self.nav_buttons_frame,
            text="Password Generator",
            command=self.show_generator,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w"
        )
        self.generator_button.pack(fill="x", pady=5)
        
        # Shared passwords button
        self.shared_button = ctk.CTkButton(
            self.nav_buttons_frame,
            text="Shared Passwords",
            command=self.show_shared_passwords,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w"
        )
        self.shared_button.pack(fill="x", pady=5)
        
        # Settings button
        self.settings_button = ctk.CTkButton(
            self.nav_buttons_frame,
            text="Settings",
            command=self.show_settings,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w"
        )
        self.settings_button.pack(fill="x", pady=5)
        
        # Spacer
        self.sidebar_spacer = ctk.CTkFrame(self.sidebar, fg_color="transparent", height=20)
        self.sidebar_spacer.pack(fill="x", expand=True)
        
        # Logout button at bottom
        self.logout_button = ctk.CTkButton(
            self.sidebar,
            text="Logout",
            command=self.handle_logout,
            fg_color="transparent",
            text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30")
        )
        self.logout_button.pack(fill="x", padx=10, pady=10)
    
    def create_header(self):
        """Create the header with search and filter options."""
        self.header_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Configure header grid
        self.header_frame.grid_columnconfigure(0, weight=0)  # Category dropdown
        self.header_frame.grid_columnconfigure(1, weight=1)  # Search box
        
        # Category filter dropdown
        self.category_label = ctk.CTkLabel(
            self.header_frame,
            text="Category:"
        )
        self.category_label.grid(row=0, column=0, padx=(0, 5))
        
        self.category_var = ctk.StringVar(value="All")
        self.category_dropdown = ctk.CTkOptionMenu(
            self.header_frame,
            variable=self.category_var,
            values=["All"],
            command=self.filter_by_category
        )
        self.category_dropdown.grid(row=0, column=1, padx=5)
        
        # Search box
        self.search_entry = ctk.CTkEntry(
            self.header_frame,
            placeholder_text="Search passwords..."
        )
        self.search_entry.grid(row=0, column=2, padx=5, sticky="ew")
        self.search_entry.bind("<KeyRelease>", self.handle_search)
        
        # Search button
        self.search_button = ctk.CTkButton(
            self.header_frame,
            text="Search",
            width=80,
            command=self.handle_search_button
        )
        self.search_button.grid(row=0, column=3, padx=(5, 0))
    
    def create_password_list(self):
        """Create the scrollable frame for password entries."""
        # Container frame for the scrollable area
        self.list_container = ctk.CTkFrame(self.content_frame)
        self.list_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.list_container.grid_columnconfigure(0, weight=1)
        self.list_container.grid_rowconfigure(0, weight=1)
        
        # Scrollable frame for password entries
        self.scrollable_frame = ctk.CTkScrollableFrame(self.list_container)
        self.scrollable_frame.grid(row=0, column=0, sticky="nsew")
        
        # Empty state label
        self.empty_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="No passwords saved yet. Click + to add a new password.",
            font=("Roboto", 12),
            text_color=("gray40", "gray60")
        )
        
        # Frame to contain active tool (generator or settings)
        self.tool_frame = ctk.CTkFrame(self.content_frame)
    
    def create_add_button(self):
        """Create the floating action button for adding passwords."""
        self.add_button = ctk.CTkButton(
            self,
            text="+",
            width=50,
            height=50,
            corner_radius=25,
            font=("Roboto", 20, "bold"),
            command=self.show_add_password_dialog
        )
        
        # Position in bottom right corner (will be placed in after_idle)
        self.after(100, self.position_add_button)
    
    def position_add_button(self):
        """Position the add button in the bottom right corner."""
        self.update_idletasks()  # Ensure geometry is updated
        x = self.winfo_width() - 70
        y = self.winfo_height() - 70
        self.add_button.place(x=x, y=y)
    
    def load_passwords(self):
        """Load encrypted passwords from storage."""
        encrypted_data = self.storage_manager.load_encrypted_passwords()
        
        if encrypted_data:
            try:
                decrypted_data = self.crypto_manager.decrypt_data(encrypted_data)
                if decrypted_data and isinstance(decrypted_data, dict) and "entries" in decrypted_data:
                    self.password_entries = decrypted_data["entries"]
                    
                    # Extract categories
                    categories = set(["All"])
                    for entry in self.password_entries:
                        if "category" in entry and entry["category"]:
                            categories.add(entry["category"])
                    
                    self.categories = sorted(list(categories))
                    self.update_category_dropdown()
                else:
                    self.password_entries = []
            except Exception as e:
                print(f"Error decrypting passwords: {e}")
                self.password_entries = []
        else:
            self.password_entries = []
            
        # Display passwords
        self.display_filtered_passwords()
    
    def save_passwords(self):
        """Save passwords to encrypted storage."""
        data = {
            "entries": self.password_entries,
            "version": 1
        }
        
        encrypted_data = self.crypto_manager.encrypt_data(data)
        return self.storage_manager.save_encrypted_passwords(encrypted_data)
    
    def update_category_dropdown(self):
        """Update the category dropdown with available categories."""
        current_value = self.category_var.get()
        self.category_dropdown.configure(values=self.categories)
        
        # If current value is no longer in the list, reset to "All"
        if current_value not in self.categories:
            self.category_var.set("All")
    
    def filter_by_category(self, category):
        """Filter password list by selected category."""
        self.selected_category = category
        self.display_filtered_passwords()
    
    def handle_search(self, event=None):
        """Handle search input."""
        self.search_text = self.search_entry.get().lower()
        self.display_filtered_passwords()
    
    def handle_search_button(self):
        """Handle search button click."""
        self.search_text = self.search_entry.get().lower()
        self.display_filtered_passwords()
    
    def get_filtered_passwords(self):
        """Get filtered password entries based on category and search text."""
        filtered = []
        
        for entry in self.password_entries:
            # Category filter
            if self.selected_category != "All" and entry.get("category", "") != self.selected_category:
                continue
                
            # Search filter
            if self.search_text:
                title = entry.get("title", "").lower()
                username = entry.get("username", "").lower()
                website = entry.get("website", "").lower()
                category = entry.get("category", "").lower()
                notes = entry.get("notes", "").lower()
                
                search_fields = [title, username, website, category, notes]
                if not any(self.search_text in field for field in search_fields):
                    continue
                    
            filtered.append(entry)
            
        return filtered
    
    def display_filtered_passwords(self):
        """Display filtered password entries in the UI."""
        # Clear current list
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
            
        filtered_entries = self.get_filtered_passwords()
        
        if not filtered_entries:
            if self.search_text or self.selected_category != "All":
                # No results from search/filter
                self.empty_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text="No passwords match your search.",
                    font=("Roboto", 12),
                    text_color=("gray40", "gray60")
                )
            else:
                # No passwords at all
                self.empty_label = ctk.CTkLabel(
                    self.scrollable_frame,
                    text="No passwords saved yet. Click + to add a new password.",
                    font=("Roboto", 12),
                    text_color=("gray40", "gray60")
                )
            self.empty_label.pack(pady=50)
        else:
            # Display entries
            for i, entry in enumerate(filtered_entries):
                self.create_password_item(entry, i)
    
    def create_password_item(self, entry, index):
        """Create a single password entry item in the list."""
        # Container frame for the entry
        item_frame = ctk.CTkFrame(self.scrollable_frame)
        item_frame.pack(fill="x", pady=(0, 10), padx=5)
        
        # Configure grid
        item_frame.grid_columnconfigure(0, weight=1)
        item_frame.grid_columnconfigure(1, weight=0)
        
        # Title and website
        title_text = entry.get("title", "Untitled")
        website_text = entry.get("website", "")
        
        title_label = ctk.CTkLabel(
            item_frame,
            text=title_text,
            font=("Roboto", 14, "bold"),
            anchor="w"
        )
        title_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 0))
        
        if website_text:
            website_label = ctk.CTkLabel(
                item_frame,
                text=website_text,
                font=("Roboto", 12),
                text_color=("gray40", "gray60"),
                anchor="w"
            )
            website_label.grid(row=1, column=0, sticky="w", padx=10, pady=(0, 5))
        
        # Username preview
        username_text = entry.get("username", "")
        if username_text:
            username_label = ctk.CTkLabel(
                item_frame,
                text=f"Username: {username_text}",
                font=("Roboto", 12),
                anchor="w"
            )
            username_label.grid(row=2, column=0, sticky="w", padx=10, pady=(0, 10))
        
        # Category badge if available
        category_text = entry.get("category", "")
        if category_text:
            category_badge = ctk.CTkLabel(
                item_frame,
                text=category_text,
                font=("Roboto", 10),
                fg_color=("gray80", "gray30"),
                corner_radius=10,
                padx=8,
                pady=2
            )
            category_badge.grid(row=0, column=1, padx=(0, 10), pady=(10, 0))
        
        # Button frame
        button_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
        button_frame.grid(row=3, column=0, columnspan=2, sticky="e", padx=10, pady=(0, 10))
        
        # View button
        view_button = ctk.CTkButton(
            button_frame,
            text="View",
            width=70,
            command=lambda e=entry: self.view_password(e)
        )
        view_button.pack(side="right", padx=(5, 0))
        
        # Make the whole item clickable
        for widget in [item_frame, title_label]:
            widget.bind("<Button-1>", lambda event, e=entry: self.view_password(e))
            widget.configure(cursor="hand2")
    
    def view_password(self, entry):
        """Show dialog to view a password entry."""
        # Create a top level window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Password Details")
        dialog.geometry("500x650")
        dialog.transient(self.winfo_toplevel())  # Set to be on top of the main window
        dialog.grab_set()  # Make window modal
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Main container
        container = ctk.CTkFrame(dialog, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Create entry detail frame
        entry_frame = PasswordEntryFrame(
            container,
            self.crypto_manager,
            entry=entry,
            on_save=self.save_edited_password,
            on_delete=self.delete_password,
            categories=self.categories,
            password_generator=self.password_generator
        )
        entry_frame.pack(fill="both", expand=True)
        
        # Add share button at bottom
        share_frame = ctk.CTkFrame(container, fg_color="transparent")
        share_frame.pack(fill="x", pady=(10, 0))
        
        share_button = ctk.CTkButton(
            share_frame,
            text="Share Password Securely",
            font=("Roboto", 14),
            height=40,
            command=lambda: self.show_share_dialog(entry)
        )
        share_button.pack(fill="x")
    
    def show_add_password_dialog(self):
        """Show dialog to add a new password."""
        # Create a top level window
        dialog = ctk.CTkToplevel(self)
        dialog.title("Add Password")
        dialog.geometry("500x600")
        dialog.transient(self)  # Set to be on top of the main window
        dialog.grab_set()  # Make window modal
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        # Create entry detail frame
        entry_frame = PasswordEntryFrame(
            dialog,
            self.crypto_manager,
            on_save=self.add_new_password,
            categories=self.categories,
            password_generator=self.password_generator
        )
        entry_frame.pack(fill="both", expand=True, padx=10, pady=10)
    
    def add_new_password(self, entry):
        """Add a new password entry."""
        # Add the entry to the list
        self.password_entries.append(entry)
        
        # Update categories if needed
        if "category" in entry and entry["category"] and entry["category"] not in self.categories:
            self.categories.append(entry["category"])
            self.categories.sort()
            self.update_category_dropdown()
        
        # Save passwords
        self.save_passwords()
        
        # Refresh display
        self.display_filtered_passwords()
    
    def save_edited_password(self, old_entry, new_entry):
        """Save changes to an existing password entry."""
        # Find the entry in the list
        for i, entry in enumerate(self.password_entries):
            if entry is old_entry:
                self.password_entries[i] = new_entry
                break
        
        # Update categories if needed
        if "category" in new_entry and new_entry["category"] and new_entry["category"] not in self.categories:
            self.categories.append(new_entry["category"])
            self.categories.sort()
            self.update_category_dropdown()
        
        # Save passwords
        self.save_passwords()
        
        # Refresh display
        self.display_filtered_passwords()
    
    def delete_password(self, entry):
        """Delete a password entry."""
        # Remove the entry from the list
        self.password_entries.remove(entry)
        
        # Update categories
        self.update_categories_after_delete()
        
        # Save passwords
        self.save_passwords()
        
        # Refresh display
        self.display_filtered_passwords()
    
    def update_categories_after_delete(self):
        """Update the category list after deleting an entry."""
        # Get all categories still in use
        categories = set(["All"])
        for entry in self.password_entries:
            if "category" in entry and entry["category"]:
                categories.add(entry["category"])
        
        self.categories = sorted(list(categories))
        self.update_category_dropdown()
    
    def show_passwords_list(self):
        """Show the main passwords list view."""
        # Highlight the active button
        self.passwords_button.configure(fg_color=("gray75", "gray25"))
        self.generator_button.configure(fg_color="transparent")
        self.shared_button.configure(fg_color="transparent")
        self.settings_button.configure(fg_color="transparent")
        
        # Show the password list
        if hasattr(self, 'tool_frame'):
            self.tool_frame.grid_forget()
        
        self.list_container.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        self.header_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        
        # Show add button
        self.position_add_button()
        
        # Refresh list
        self.display_filtered_passwords()
    
    def show_generator(self):
        """Show the password generator tool."""
        # Highlight the active button
        self.passwords_button.configure(fg_color="transparent")
        self.generator_button.configure(fg_color=("gray75", "gray25"))
        self.shared_button.configure(fg_color="transparent")
        self.settings_button.configure(fg_color="transparent")
        
        # Hide the password list
        self.list_container.grid_forget()
        self.header_frame.grid_forget()
        
        # Hide add button
        self.add_button.place_forget()
        
        # Show generator
        if hasattr(self, 'tool_frame'):
            self.tool_frame.grid_forget()
        
        self.tool_frame = GeneratorFrame(
            self.content_frame,
            self.password_generator
        )
        self.tool_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
    
    def show_settings(self):
        """Show the settings view."""
        # Highlight the active button
        self.passwords_button.configure(fg_color="transparent")
        self.generator_button.configure(fg_color="transparent")
        self.shared_button.configure(fg_color="transparent")
        self.settings_button.configure(fg_color=("gray75", "gray25"))
        
        # Hide the password list
        self.list_container.grid_forget()
        self.header_frame.grid_forget()
        
        # Hide add button
        self.add_button.place_forget()
        
        # Show settings
        if hasattr(self, 'tool_frame'):
            self.tool_frame.grid_forget()
        
        self.tool_frame = SettingsFrame(
            self.content_frame,
            self.theme_manager,
            self.storage_manager
        )
        self.tool_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
        
    def show_shared_passwords(self):
        """Show the shared passwords section."""
        # Highlight the active button
        self.passwords_button.configure(fg_color="transparent")
        self.generator_button.configure(fg_color="transparent")
        self.shared_button.configure(fg_color=("gray75", "gray25"))
        self.settings_button.configure(fg_color="transparent")
        
        # Hide the password list
        self.list_container.grid_forget()
        self.header_frame.grid_forget()
        
        # Hide add button
        self.add_button.place_forget()
        
        # Show shared passwords
        if hasattr(self, 'tool_frame'):
            self.tool_frame.grid_forget()
        
        self.tool_frame = SharedPasswordsFrame(
            self.content_frame,
            self.sharing_manager
        )
        self.tool_frame.grid(row=0, column=0, rowspan=2, sticky="nsew", padx=10, pady=10)
    
    def handle_logout(self):
        """Handle logout button click."""
        # Confirm logout
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Logout")
        dialog.geometry("300x150")
        dialog.transient(self)
        dialog.grab_set()
        
        # Center the dialog
        dialog.update_idletasks()
        x = self.winfo_rootx() + (self.winfo_width() // 2) - (dialog.winfo_width() // 2)
        y = self.winfo_rooty() + (self.winfo_height() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")
        
        label = ctk.CTkLabel(
            dialog,
            text="Are you sure you want to logout?\nAll unsaved changes will be lost.",
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
            text="Logout",
            width=100,
            fg_color="#e74c3c",
            hover_color="#c0392b",
            command=lambda: self.confirm_logout(dialog)
        )
        confirm_button.pack(side="right", padx=10)
    
    def confirm_logout(self, dialog):
        """Complete the logout process."""
        dialog.destroy()
        self.on_logout()
        
    def show_share_dialog(self, entry):
        """Show dialog to share a password securely."""
        dialog = ShareDialog(self.parent, self.sharing_manager, entry)
