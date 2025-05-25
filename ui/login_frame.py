import customtkinter as ctk
from ui.app_icons import get_lock_icon

class LoginFrame(ctk.CTkFrame):
    """Frame for user login or initial setup."""
    
    def __init__(self, parent, auth_manager, on_login_success):
        super().__init__(parent)
        self.parent = parent
        self.auth_manager = auth_manager
        self.on_login_success = on_login_success
        
        # Check if this is first run
        self.is_first_run = self.auth_manager.is_first_run()
        
        # Create UI elements
        self.create_widgets()
        
    def create_widgets(self):
        """Create and position all UI widgets."""
        # Title and icon
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(50, 20), padx=20, fill="x")
        
        lock_icon = get_lock_icon(size=64)
        self.icon_label = ctk.CTkLabel(self.header_frame, text="", image=lock_icon)
        self.icon_label.pack()
        
        title_text = "Create Master Password" if self.is_first_run else "Enter Master Password"
        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text=title_text,
            font=("Roboto", 24, "bold")
        )
        self.title_label.pack(pady=(10, 0))
        
        description_text = (
            "This password will be used to secure all your passwords.\n"
            "Make sure it's strong and memorable - you cannot recover it if forgotten!"
        ) if self.is_first_run else "Enter your master password to unlock the password manager"
        
        self.description_label = ctk.CTkLabel(
            self.header_frame,
            text=description_text,
            font=("Roboto", 12),
            text_color=("gray50", "gray70")
        )
        self.description_label.pack(pady=(5, 0))
        
        # Main content frame
        self.content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.content_frame.pack(pady=20, padx=20, fill="both", expand=True)
        
        # Center the login form
        self.content_frame.grid_columnconfigure(0, weight=1)
        self.content_frame.grid_columnconfigure(2, weight=1)
        
        self.form_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        self.form_frame.grid(row=0, column=1, pady=20)
        
        # Password fields
        self.password_label = ctk.CTkLabel(
            self.form_frame, 
            text="Master Password:",
            font=("Roboto", 12, "bold")
        )
        self.password_label.pack(anchor="w", pady=(0, 5))
        
        self.password_entry = ctk.CTkEntry(
            self.form_frame, 
            width=300, 
            placeholder_text="Enter your master password",
            show="•"
        )
        self.password_entry.pack(pady=(0, 15))
        
        # For first run, add confirmation field
        if self.is_first_run:
            self.confirm_label = ctk.CTkLabel(
                self.form_frame, 
                text="Confirm Password:",
                font=("Roboto", 12, "bold")
            )
            self.confirm_label.pack(anchor="w", pady=(0, 5))
            
            self.confirm_entry = ctk.CTkEntry(
                self.form_frame, 
                width=300,
                placeholder_text="Confirm your master password",
                show="•"
            )
            self.confirm_entry.pack(pady=(0, 15))
        
        # Show password checkbox
        self.show_password_var = ctk.BooleanVar(value=False)
        self.show_password_cb = ctk.CTkCheckBox(
            self.form_frame,
            text="Show password",
            variable=self.show_password_var,
            command=self.toggle_password_visibility
        )
        self.show_password_cb.pack(anchor="w", pady=(0, 20))
        
        # Button
        button_text = "Create Password" if self.is_first_run else "Unlock"
        self.submit_button = ctk.CTkButton(
            self.form_frame,
            text=button_text,
            width=300,
            command=self.handle_submit
        )
        self.submit_button.pack(pady=(5, 0))
        
        # Error message
        self.error_label = ctk.CTkLabel(
            self.form_frame,
            text="",
            text_color=("red", "#FF5555"),
            font=("Roboto", 11)
        )
        self.error_label.pack(pady=(10, 0))
        
        # Bind enter key
        self.password_entry.bind("<Return>", lambda event: self.handle_submit())
        if self.is_first_run:
            self.confirm_entry.bind("<Return>", lambda event: self.handle_submit())
            
        # Set focus
        self.password_entry.focus_set()
        
    def toggle_password_visibility(self):
        """Toggle password visibility."""
        show_char = "" if self.show_password_var.get() else "•"
        self.password_entry.configure(show=show_char)
        if self.is_first_run:
            self.confirm_entry.configure(show=show_char)
    
    def handle_submit(self):
        """Handle button click based on whether this is first run or login."""
        if self.is_first_run:
            self.handle_create_password()
        else:
            self.handle_login()
    
    def handle_create_password(self):
        """Handle creating a new master password."""
        password = self.password_entry.get()
        confirm = self.confirm_entry.get()
        
        # Validate passwords
        if not password:
            self.show_error("Password cannot be empty")
            return
            
        if password != confirm:
            self.show_error("Passwords do not match")
            return
            
        if len(password) < 8:
            self.show_error("Password must be at least 8 characters long")
            return
            
        # Create the master password
        if self.auth_manager.create_master_password(password):
            # Get the derived key
            _, key = self.auth_manager.verify_master_password(password)
            self.on_login_success(key)
        else:
            self.show_error("Failed to create master password")
    
    def handle_login(self):
        """Handle login with existing master password."""
        password = self.password_entry.get()
        
        if not password:
            self.show_error("Please enter your master password")
            return
            
        # Verify the master password
        is_valid, key = self.auth_manager.verify_master_password(password)
        
        if is_valid:
            self.on_login_success(key)
        else:
            self.show_error("Invalid master password")
    
    def show_error(self, message):
        """Display an error message."""
        self.error_label.configure(text=message)
