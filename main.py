import os
import customtkinter as ctk
from ui.login_frame import LoginFrame
from ui.dashboard_frame import DashboardFrame
from auth_manager import AuthManager
from crypto_manager import CryptoManager
from storage_manager import StorageManager
from ui.theme_manager import ThemeManager

class PasswordManagerApp(ctk.CTk):
    """Main application class for the password manager."""
    
    def __init__(self):
        super().__init__()
        
        # Initialize app
        self.title("SecurePass Manager")
        self.geometry("900x600")
        self.minsize(800, 500)
        
        # Initialize managers
        self.storage_manager = StorageManager()
        self.auth_manager = AuthManager(self.storage_manager)
        self.crypto_manager = None  # Will be initialized after login
        self.theme_manager = ThemeManager(self)
        
        # Initialize UI frames
        self.current_frame = None
        self.show_login_frame()
        
        # Center window
        self.center_window()

    def center_window(self):
        """Center the window on the screen."""
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry('{}x{}+{}+{}'.format(width, height, x, y))
        
    def show_login_frame(self):
        """Display the login frame."""
        if self.current_frame:
            self.current_frame.pack_forget()
            
        self.login_frame = LoginFrame(self, self.auth_manager, self.on_login_success)
        self.login_frame.pack(fill=ctk.BOTH, expand=True)
        self.current_frame = self.login_frame
        
    def show_dashboard_frame(self):
        """Display the dashboard frame."""
        if self.current_frame:
            self.current_frame.pack_forget()
            
        self.dashboard_frame = DashboardFrame(
            self, 
            self.crypto_manager, 
            self.storage_manager,
            self.theme_manager,
            self.on_logout
        )
        self.dashboard_frame.pack(fill=ctk.BOTH, expand=True)
        self.current_frame = self.dashboard_frame
        
    def on_login_success(self, master_key):
        """Handle successful login."""
        # Initialize crypto manager with the master key
        self.crypto_manager = CryptoManager(master_key)
        self.show_dashboard_frame()
        
    def on_logout(self):
        """Handle logout."""
        # Clear sensitive data
        self.crypto_manager = None
        self.show_login_frame()

if __name__ == "__main__":
    # Set appearance mode
    ctk.set_appearance_mode("System")  # Default to system theme
    ctk.set_default_color_theme("blue")
    
    # Create and run app
    app = PasswordManagerApp()
    app.mainloop()
