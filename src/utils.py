"""
Utility functions for DocuMind application.
"""

import logging
import base64
import json
from datetime import datetime
from typing import Any, Dict, Optional
import streamlit as st

def setup_logging(level: str = "INFO") -> logging.Logger:
    """Setup logging configuration."""
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('documind.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)

def create_download_link(data: Any, filename: str, mime_type: str = "text/plain") -> str:
    """Create a download link for Streamlit."""
    if isinstance(data, dict):
        data = json.dumps(data, indent=2)
    elif not isinstance(data, str):
        data = str(data)
    
    b64 = base64.b64encode(data.encode()).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'

def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def validate_file_upload(uploaded_file) -> tuple[bool, str]:
    """Validate uploaded file."""
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file size (50MB limit)
    file_size = len(uploaded_file.getvalue()) / (1024 * 1024)  # Convert to MB
    if file_size > 50:
        return False, f"File size ({file_size:.1f}MB) exceeds limit (50MB)"
    
    # Check file type
    supported_types = ['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp']
    file_extension = uploaded_file.name.lower().split('.')[-1]
    if file_extension not in supported_types:
        return False, f"Unsupported file type: {file_extension}"
    
    return True, "File is valid"

def generate_timestamp() -> str:
    """Generate a formatted timestamp."""
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def safe_json_serialize(obj: Any) -> str:
    """Safely serialize objects to JSON."""
    def default_serializer(obj):
        if hasattr(obj, 'isoformat'):
            return obj.isoformat()
        elif hasattr(obj, '__dict__'):
            return obj.__dict__
        else:
            return str(obj)
    
    return json.dumps(obj, default=default_serializer, indent=2)

def extract_text_safely(text: str, max_length: int = 1000) -> str:
    """Safely extract and truncate text."""
    if not text:
        return ""
    
    # Remove extra whitespace
    text = " ".join(text.split())
    
    # Truncate if too long
    if len(text) > max_length:
        text = text[:max_length] + "..."
    
    return text

def create_metric_card(title: str, value: str, delta: Optional[str] = None):
    """Create a styled metric card."""
    st.markdown(f"""
    <div class="metric-card">
        <h4>{title}</h4>
        <h2>{value}</h2>
        {f'<p style="color: green;">{delta}</p>' if delta else ''}
    </div>
    """, unsafe_allow_html=True)

def show_error_with_details(error: Exception, context: str = ""):
    """Display error with details in a user-friendly way."""
    st.error(f"❌ {context}: {str(error)}")
    if st.checkbox("Show technical details"):
        st.code(f"Error Type: {type(error).__name__}\nError: {str(error)}")

def create_progress_bar(progress: float, text: str = "Processing..."):
    """Create a custom progress bar."""
    st.progress(progress)
    st.caption(text)

def format_duration(seconds: float) -> str:
    """Format duration in human readable format."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"
