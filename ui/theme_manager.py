import customtkinter as ctk

class ThemeManager:
    """Manages theme settings for the application."""
    
    def __init__(self, app):
        """
        Initialize the theme manager.
        
        Args:
            app: The main application instance
        """
        self.app = app
        self.current_mode = "system"
    
    def set_theme_mode(self, mode):
        """
        Set the theme mode.
        
        Args:
            mode: Theme mode ("light", "dark", or "system")
        """
        if mode not in ["light", "dark", "system"]:
            mode = "system"
            
        self.current_mode = mode
        ctk.set_appearance_mode(mode)
        
        # Save setting
        settings = self.app.storage_manager.get_app_settings()
        settings["theme_mode"] = mode
        self.app.storage_manager.save_app_settings(settings)
    
    def get_current_mode(self):
        """
        Get the current theme mode.
        
        Returns:
            str: Current theme mode
        """
        return self.current_mode
    
    def toggle_mode(self):
        """Toggle between light and dark mode."""
        current = self.current_mode
        if current == "light":
            self.set_theme_mode("dark")
        elif current == "dark":
            self.set_theme_mode("light")
        else:
            # If system, check what's the current actual mode and toggle from that
            actual_mode = ctk.get_appearance_mode().lower()
            if actual_mode == "light":
                self.set_theme_mode("dark")
            else:
                self.set_theme_mode("light")
