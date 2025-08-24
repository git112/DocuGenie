"""
Configuration management for DocuGenie application.
"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for DocuGenie application."""
    
    def __init__(self):
        # API Keys
        self.google_api_key: str = os.getenv("GOOGLE_API_KEY", "")
        self.openai_api_key: str = os.getenv("OPENAI_API_KEY", "")
        
        # Gemini Configuration
        self.gemini_model: str = "gemini-2.5-pro"
        self.gemini_temperature: float = 0.1
        self.gemini_max_tokens: int = 8192
        
        # Document Processing
        self.max_file_size_mb: int = 50
        self.supported_formats: list = ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp']
        self.ocr_confidence_threshold: float = 0.7
        
        # Application Settings
        self.debug_mode: bool = os.getenv("DEBUG", "False").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "INFO")
        self.cache_enabled: bool = os.getenv("CACHE_ENABLED", "True").lower() == "true"
        
        # Export Settings
        self.export_formats: list = ['json', 'excel', 'txt', 'pdf']
        self.max_export_size_mb: int = 10
        
        # UI Settings
        self.page_title: str = "DocuGenie - AI Document Intelligence"
        self.page_icon: str = "📑"
        self.layout: str = "wide"
        
    def validate_config(self) -> bool:
        """Validate that required configuration is present."""
        if not self.google_api_key:
            raise ValueError("GOOGLE_API_KEY is required. Please set it in your .env file.")
        return True
    
    def get_gemini_config(self) -> dict:
        """Get Gemini model configuration."""
        return {
            "model": self.gemini_model,
            "temperature": self.gemini_temperature,
            "max_tokens": self.gemini_max_tokens,
            "api_key": self.google_api_key
        }
    
    def get_supported_formats_str(self) -> str:
        """Get supported formats as comma-separated string."""
        return ", ".join(self.supported_formats)
    
    def is_file_supported(self, filename: str) -> bool:
        """Check if file format is supported."""
        if not filename:
            return False
        extension = filename.lower().split('.')[-1]
        return extension in self.supported_formats
