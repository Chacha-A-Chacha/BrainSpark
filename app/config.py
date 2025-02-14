class Config:
    """Configuration settings for the application."""
    
    DEBUG = True  # Enable or disable debug mode
    TESTING = False  # Enable or disable testing mode
    DATABASE_URI = 'sqlite:///myapp.db'  # Database connection string
    SECRET_KEY = 'your_secret_key'  # Secret key for session management
    ALLOWED_HOSTS = ['localhost', '127.0.0.1']  # Allowed hosts for the application
    PORT = 5000  # Port to run the application on

    @staticmethod
    def init_app(app):
        """Initialize the app with the configuration."""
        pass  # Additional initialization can be added here if needed