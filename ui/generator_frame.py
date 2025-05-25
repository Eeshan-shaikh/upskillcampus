import customtkinter as ctk
import pyperclip
import threading
import tkinter as tk

class GeneratorFrame(ctk.CTkFrame):
    """Frame for password generation tool."""
    
    def __init__(self, parent, password_generator):
        super().__init__(parent)
        self.parent = parent
        self.password_generator = password_generator
        
        # Default settings
        self.length = 16
        self.include_uppercase = True
        self.include_lowercase = True
        self.include_numbers = True
        self.include_symbols = True
        self.exclude_similar = False
        self.exclude_ambiguous = False
        
        # Create UI
        self.create_widgets()
    
    def create_widgets(self):
        """Create all widgets for the generator frame."""
        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        
        # Title
        self.title_label = ctk.CTkLabel(
            self,
            text="Password Generator",
            font=("Roboto", 20, "bold")
        )
        self.title_label.grid(row=0, column=0, sticky="w", padx=20, pady=(20, 30))
        
        # Generator options frame
        self.options_frame = ctk.CTkFrame(self)
        self.options_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Configure options grid
        self.options_frame.grid_columnconfigure(0, weight=1)
        self.options_frame.grid_columnconfigure(1, weight=1)
        
        # Password length slider
        self.length_label = ctk.CTkLabel(
            self.options_frame,
            text=f"Password Length: {self.length}",
            font=("Roboto", 12, "bold")
        )
        self.length_label.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.length_slider = ctk.CTkSlider(
            self.options_frame,
            from_=8,
            to=32,
            number_of_steps=24,
            command=self.update_length
        )
        self.length_slider.grid(row=1, column=0, columnspan=2, sticky="ew", padx=10, pady=(0, 15))
        self.length_slider.set(self.length)
        
        # Character options
        options_label = ctk.CTkLabel(
            self.options_frame,
            text="Character Options:",
            font=("Roboto", 12, "bold")
        )
        options_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=10, pady=(0, 5))
        
        # Left column of options
        self.uppercase_var = ctk.BooleanVar(value=self.include_uppercase)
        self.uppercase_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Include Uppercase (A-Z)",
            variable=self.uppercase_var,
            command=self.update_options
        )
        self.uppercase_cb.grid(row=3, column=0, sticky="w", padx=10, pady=5)
        
        self.lowercase_var = ctk.BooleanVar(value=self.include_lowercase)
        self.lowercase_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Include Lowercase (a-z)",
            variable=self.lowercase_var,
            command=self.update_options
        )
        self.lowercase_cb.grid(row=4, column=0, sticky="w", padx=10, pady=5)
        
        # Right column of options
        self.numbers_var = ctk.BooleanVar(value=self.include_numbers)
        self.numbers_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Include Numbers (0-9)",
            variable=self.numbers_var,
            command=self.update_options
        )
        self.numbers_cb.grid(row=3, column=1, sticky="w", padx=10, pady=5)
        
        self.symbols_var = ctk.BooleanVar(value=self.include_symbols)
        self.symbols_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Include Symbols (!@#$%...)",
            variable=self.symbols_var,
            command=self.update_options
        )
        self.symbols_cb.grid(row=4, column=1, sticky="w", padx=10, pady=5)
        
        # Additional options
        additional_label = ctk.CTkLabel(
            self.options_frame,
            text="Additional Options:",
            font=("Roboto", 12, "bold")
        )
        additional_label.grid(row=5, column=0, columnspan=2, sticky="w", padx=10, pady=(15, 5))
        
        self.similar_var = ctk.BooleanVar(value=self.exclude_similar)
        self.similar_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Exclude Similar Characters (i, l, 1, L, o, 0, O)",
            variable=self.similar_var,
            command=self.update_options
        )
        self.similar_cb.grid(row=6, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        self.ambiguous_var = ctk.BooleanVar(value=self.exclude_ambiguous)
        self.ambiguous_cb = ctk.CTkCheckBox(
            self.options_frame,
            text="Exclude Ambiguous Characters ({ } [ ] ( ) / \\ ' \" ` ~ , ; : . < >)",
            variable=self.ambiguous_var,
            command=self.update_options
        )
        self.ambiguous_cb.grid(row=7, column=0, columnspan=2, sticky="w", padx=10, pady=5)
        
        # Generated password display
        self.password_frame = ctk.CTkFrame(self)
        self.password_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.password_frame.grid_columnconfigure(0, weight=1)
        
        self.password_label = ctk.CTkLabel(
            self.password_frame,
            text="Generated Password:",
            font=("Roboto", 12, "bold")
        )
        self.password_label.grid(row=0, column=0, sticky="w", padx=10, pady=(10, 5))
        
        # Password display with copy button
        self.password_display_frame = ctk.CTkFrame(self.password_frame, fg_color="transparent")
        self.password_display_frame.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))
        self.password_display_frame.grid_columnconfigure(0, weight=1)
        
        self.password_entry = ctk.CTkEntry(
            self.password_display_frame,
            font=("Roboto", 14),
            height=40
        )
        self.password_entry.grid(row=0, column=0, sticky="ew", padx=(0, 10))
        
        self.copy_button = ctk.CTkButton(
            self.password_display_frame,
            text="Copy",
            width=80,
            command=self.copy_password
        )
        self.copy_button.grid(row=0, column=1)
        
        # Password strength indicator
        self.strength_frame = ctk.CTkFrame(self.password_frame)
        self.strength_frame.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 10))
        
        self.strength_label = ctk.CTkLabel(
            self.strength_frame,
            text="Password Strength:",
            font=("Roboto", 12, "bold")
        )
        self.strength_label.pack(anchor="w", padx=10, pady=(5, 0))
        
        self.strength_bar_frame = ctk.CTkFrame(self.strength_frame, fg_color="transparent")
        self.strength_bar_frame.pack(fill="x", padx=10, pady=(5, 0))
        
        self.strength_bar = ctk.CTkProgressBar(self.strength_bar_frame)
        self.strength_bar.pack(fill="x")
        
        self.strength_text = ctk.CTkLabel(
            self.strength_frame,
            text="",
            font=("Roboto", 11),
            text_color=("gray40", "gray60")
        )
        self.strength_text.pack(anchor="w", padx=10, pady=(5, 10))
        
        # Generate button
        self.generate_button = ctk.CTkButton(
            self,
            text="Generate Password",
            font=("Roboto", 14, "bold"),
            height=50,
            command=self.generate_password
        )
        self.generate_button.grid(row=3, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # Notification area for copy confirmation
        self.notification_frame = ctk.CTkFrame(self)
        self.notification_label = ctk.CTkLabel(
            self.notification_frame,
            text="",
            font=("Roboto", 12)
        )
        self.notification_label.pack(pady=5)
        
        # Generate an initial password
        self.generate_password()
    
    def update_length(self, value):
        """Update the password length based on slider."""
        self.length = int(value)
        self.length_label.configure(text=f"Password Length: {self.length}")
    
    def update_options(self):
        """Update password options based on checkboxes."""
        self.include_uppercase = self.uppercase_var.get()
        self.include_lowercase = self.lowercase_var.get()
        self.include_numbers = self.numbers_var.get()
        self.include_symbols = self.symbols_var.get()
        self.exclude_similar = self.similar_var.get()
        self.exclude_ambiguous = self.ambiguous_var.get()
        
        # Ensure at least one character type is selected
        if not any([self.include_uppercase, self.include_lowercase, 
                   self.include_numbers, self.include_symbols]):
            # If none are selected, re-enable lowercase as a default
            self.include_lowercase = True
            self.lowercase_var.set(True)
    
    def generate_password(self):
        """Generate a password with current settings."""
        try:
            password = self.password_generator.generate_password(
                length=self.length,
                include_uppercase=self.include_uppercase,
                include_lowercase=self.include_lowercase,
                include_numbers=self.include_numbers,
                include_symbols=self.include_symbols,
                exclude_similar=self.exclude_similar,
                exclude_ambiguous=self.exclude_ambiguous
            )
            
            # Update the password display
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, password)
            
            # Update strength indicator
            self.update_strength_indicator(password)
            
        except ValueError as e:
            self.show_notification(str(e))
    
    def update_strength_indicator(self, password):
        """Update the password strength indicator."""
        if not password:
            self.strength_bar.set(0)
            self.strength_text.configure(text="No password generated")
            return
            
        score, feedback = self.password_generator.calculate_strength(password)
        
        # Update progress bar
        self.strength_bar.set(score / 100)
        
        # Update color based on strength
        if score >= 80:
            bar_color = "#2ecc71"  # Green
        elif score >= 60:
            bar_color = "#3498db"  # Blue
        elif score >= 40:
            bar_color = "#f39c12"  # Orange
        elif score >= 20:
            bar_color = "#e67e22"  # Dark Orange
        else:
            bar_color = "#e74c3c"  # Red
            
        self.strength_bar.configure(progress_color=bar_color)
        
        # Update feedback text
        self.strength_text.configure(text=feedback)
    
    def copy_password(self):
        """Copy the generated password to clipboard."""
        password = self.password_entry.get()
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
        self.notification_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.notification_label.configure(text=message)
        
        # Hide after 3 seconds
        self.after(3000, self.hide_notification)
    
    def hide_notification(self):
        """Hide the notification."""
        self.notification_frame.grid_forget()
