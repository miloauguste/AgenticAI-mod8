import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

class HealthcareConfig:
    """
    Configuration management for Healthcare Research Assistant
    Handles environment variables, default settings, and validation
    """
    
    def __init__(self):
        self.load_config()
        self.validate_config()
        self.setup_logging()
    
    def load_config(self):
        """Load configuration from environment variables"""
        
        # Google Gemini API Configuration
        self.GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
        
        # Database Configuration
        self.DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///healthcare_memory.db')
        self.DATABASE_BACKUP_ENABLED = os.getenv('DATABASE_BACKUP_ENABLED', 'true').lower() == 'true'
        self.DATABASE_BACKUP_INTERVAL_HOURS = int(os.getenv('DATABASE_BACKUP_INTERVAL_HOURS', '24'))
        
        # Application Configuration
        self.APP_NAME = os.getenv('APP_NAME', 'MediSyn Labs Healthcare Research Assistant')
        self.APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
        self.APP_DEBUG = os.getenv('APP_DEBUG', 'false').lower() == 'true'
        self.APP_LOG_LEVEL = os.getenv('APP_LOG_LEVEL', 'INFO')
        
        # Session Configuration
        self.DEFAULT_SESSION_TIMEOUT_MINUTES = int(os.getenv('DEFAULT_SESSION_TIMEOUT_MINUTES', '60'))
        self.MAX_QUERIES_PER_SESSION = int(os.getenv('MAX_QUERIES_PER_SESSION', '50'))
        self.AUTO_SAVE_INTERVAL_MINUTES = int(os.getenv('AUTO_SAVE_INTERVAL_MINUTES', '5'))
        
        # Memory Management
        self.MAX_SHORT_TERM_QUERIES = int(os.getenv('MAX_SHORT_TERM_QUERIES', '7'))
        self.MEMORY_CLEANUP_DAYS = int(os.getenv('MEMORY_CLEANUP_DAYS', '30'))
        self.AUTO_TRIM_MEMORY = os.getenv('AUTO_TRIM_MEMORY', 'true').lower() == 'true'
        
        # Human-in-the-Loop Configuration
        self.AUTO_APPROVAL_ENABLED = os.getenv('AUTO_APPROVAL_ENABLED', 'false').lower() == 'true'
        self.CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.7'))
        self.MEDICAL_RELEVANCE_THRESHOLD = float(os.getenv('MEDICAL_RELEVANCE_THRESHOLD', '0.8'))
        self.CRITICAL_PRIORITY_AUTO_APPROVE = os.getenv('CRITICAL_PRIORITY_AUTO_APPROVE', 'false').lower() == 'true'
        
        # Report Generation
        self.DEFAULT_REPORT_FORMAT = os.getenv('DEFAULT_REPORT_FORMAT', 'markdown')
        self.ENABLE_CSV_EXPORT = os.getenv('ENABLE_CSV_EXPORT', 'true').lower() == 'true'
        self.ENABLE_JSON_EXPORT = os.getenv('ENABLE_JSON_EXPORT', 'true').lower() == 'true'
        self.MAX_REPORT_SIZE_MB = int(os.getenv('MAX_REPORT_SIZE_MB', '10'))
        
        # Security Configuration
        self.ENABLE_ENCRYPTION = os.getenv('ENABLE_ENCRYPTION', 'true').lower() == 'true'
        self.SESSION_SECRET_KEY = os.getenv('SESSION_SECRET_KEY', 'healthcare_assistant_secret_key')
        self.API_RATE_LIMIT_PER_MINUTE = int(os.getenv('API_RATE_LIMIT_PER_MINUTE', '60'))
        
        # Logging Configuration
        self.LOG_FILE_PATH = os.getenv('LOG_FILE_PATH', 'logs/healthcare_assistant.log')
        self.LOG_ROTATION_SIZE_MB = int(os.getenv('LOG_ROTATION_SIZE_MB', '100'))
        self.LOG_RETENTION_DAYS = int(os.getenv('LOG_RETENTION_DAYS', '30'))
        
        # External Services
        self.PUBMED_API_KEY = os.getenv('PUBMED_API_KEY')
        self.CLINICAL_TRIALS_API_KEY = os.getenv('CLINICAL_TRIALS_API_KEY')
        
        # Development Settings
        self.MOCK_EXTERNAL_APIS = os.getenv('MOCK_EXTERNAL_APIS', 'true').lower() == 'true'
        self.ENABLE_DEBUG_LOGGING = os.getenv('ENABLE_DEBUG_LOGGING', 'false').lower() == 'true'
        self.STREAMLIT_SERVER_PORT = int(os.getenv('STREAMLIT_SERVER_PORT', '8501'))
    
    def validate_config(self):
        """Validate configuration values"""
        
        # Validate required API keys
        if not self.GOOGLE_API_KEY and not self.MOCK_EXTERNAL_APIS:
            raise ValueError("GOOGLE_API_KEY is required when MOCK_EXTERNAL_APIS is disabled")
        
        # Validate numeric ranges
        if not 0 < self.CONFIDENCE_THRESHOLD <= 1:
            raise ValueError("CONFIDENCE_THRESHOLD must be between 0 and 1")
        
        if not 0 < self.MEDICAL_RELEVANCE_THRESHOLD <= 1:
            raise ValueError("MEDICAL_RELEVANCE_THRESHOLD must be between 0 and 1")
        
        if self.MAX_QUERIES_PER_SESSION <= 0:
            raise ValueError("MAX_QUERIES_PER_SESSION must be positive")
        
        if self.MAX_SHORT_TERM_QUERIES <= 0:
            raise ValueError("MAX_SHORT_TERM_QUERIES must be positive")
        
        # Validate file paths
        os.makedirs(os.path.dirname(self.LOG_FILE_PATH), exist_ok=True)
    
    def setup_logging(self):
        """Setup logging configuration"""
        
        log_level = getattr(logging, self.APP_LOG_LEVEL.upper(), logging.INFO)
        
        logging.basicConfig(
            level=log_level,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.LOG_FILE_PATH),
                logging.StreamHandler()
            ]
        )
        
        # Set specific logger levels
        logging.getLogger('streamlit').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration"""
        return {
            'api_key': self.GOOGLE_API_KEY,
            'model': 'gemini-pro',
            'temperature': 0.1,
            'max_output_tokens': 2048,
            'mock_responses': self.MOCK_EXTERNAL_APIS
        }
    
    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory management configuration"""
        return {
            'max_short_term_queries': self.MAX_SHORT_TERM_QUERIES,
            'cleanup_days': self.MEMORY_CLEANUP_DAYS,
            'auto_trim': self.AUTO_TRIM_MEMORY,
            'database_url': self.DATABASE_URL
        }
    
    def get_approval_config(self) -> Dict[str, Any]:
        """Get human-in-the-loop approval configuration"""
        return {
            'auto_approval_enabled': self.AUTO_APPROVAL_ENABLED,
            'confidence_threshold': self.CONFIDENCE_THRESHOLD,
            'medical_relevance_threshold': self.MEDICAL_RELEVANCE_THRESHOLD,
            'critical_auto_approve': self.CRITICAL_PRIORITY_AUTO_APPROVE
        }
    
    def get_report_config(self) -> Dict[str, Any]:
        """Get report generation configuration"""
        return {
            'default_format': self.DEFAULT_REPORT_FORMAT,
            'enable_csv': self.ENABLE_CSV_EXPORT,
            'enable_json': self.ENABLE_JSON_EXPORT,
            'max_size_mb': self.MAX_REPORT_SIZE_MB
        }
    
    def get_security_config(self) -> Dict[str, Any]:
        """Get security configuration"""
        return {
            'enable_encryption': self.ENABLE_ENCRYPTION,
            'secret_key': self.SESSION_SECRET_KEY,
            'rate_limit': self.API_RATE_LIMIT_PER_MINUTE
        }
    
    def get_streamlit_config(self) -> Dict[str, Any]:
        """Get Streamlit configuration"""
        return {
            'port': self.STREAMLIT_SERVER_PORT,
            'debug': self.APP_DEBUG,
            'title': self.APP_NAME,
            'layout': 'wide'
        }
    
    def update_config(self, config_updates: Dict[str, Any]):
        """Update configuration values"""
        for key, value in config_updates.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Re-validate after updates
        self.validate_config()
    
    def export_config(self) -> Dict[str, Any]:
        """Export current configuration (excluding sensitive data)"""
        config_dict = {}
        
        for attr_name in dir(self):
            if not attr_name.startswith('_') and not callable(getattr(self, attr_name)):
                value = getattr(self, attr_name)
                
                # Exclude sensitive information
                if 'key' in attr_name.lower() or 'secret' in attr_name.lower():
                    config_dict[attr_name] = '***REDACTED***'
                else:
                    config_dict[attr_name] = value
        
        return config_dict
    
    def load_from_file(self, config_file: str):
        """Load configuration from JSON file"""
        import json
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                file_config = json.load(f)
            
            for key, value in file_config.items():
                if hasattr(self, key):
                    setattr(self, key, value)
            
            self.validate_config()
    
    def save_to_file(self, config_file: str):
        """Save configuration to JSON file"""
        import json
        
        config_dict = self.export_config()
        
        os.makedirs(os.path.dirname(config_file), exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config_dict, f, indent=2)

# Global configuration instance
config = HealthcareConfig()

# Configuration utility functions
def get_config() -> HealthcareConfig:
    """Get the global configuration instance"""
    return config

def reload_config():
    """Reload configuration from environment"""
    global config
    config = HealthcareConfig()

def is_development() -> bool:
    """Check if running in development mode"""
    return config.APP_DEBUG

def is_mock_mode() -> bool:
    """Check if running in mock mode for external APIs"""
    return config.MOCK_EXTERNAL_APIS

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name"""
    return logging.getLogger(name)

# Environment-specific configurations
class DevelopmentConfig(HealthcareConfig):
    """Development-specific configuration"""
    
    def __init__(self):
        super().__init__()
        self.APP_DEBUG = True
        self.MOCK_EXTERNAL_APIS = True
        self.ENABLE_DEBUG_LOGGING = True
        self.APP_LOG_LEVEL = 'DEBUG'

class ProductionConfig(HealthcareConfig):
    """Production-specific configuration"""
    
    def __init__(self):
        super().__init__()
        self.APP_DEBUG = False
        self.MOCK_EXTERNAL_APIS = False
        self.ENABLE_DEBUG_LOGGING = False
        self.APP_LOG_LEVEL = 'INFO'

class TestingConfig(HealthcareConfig):
    """Testing-specific configuration"""
    
    def __init__(self):
        super().__init__()
        self.APP_DEBUG = True
        self.MOCK_EXTERNAL_APIS = True
        self.DATABASE_URL = 'sqlite:///:memory:'
        self.APP_LOG_LEVEL = 'DEBUG'

def get_config_by_environment(env: str = None) -> HealthcareConfig:
    """Get configuration based on environment"""
    
    if env is None:
        env = os.getenv('ENVIRONMENT', 'development')
    
    if env.lower() == 'production':
        return ProductionConfig()
    elif env.lower() == 'testing':
        return TestingConfig()
    else:
        return DevelopmentConfig()