import os
import json
import base64
from datetime import datetime
from typing import Optional, Dict, Any, List
import streamlit as st
from dotenv import load_dotenv
import pandas as pd

# Import our custom modules
from src.document_processor import DocumentProcessor
from src.gemini_analyzer import GeminiAnalyzer
from src.utils import setup_logging, create_download_link
from src.config import Config

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

# Initialize configuration
config = Config()

# Page configuration
st.set_page_config(
    page_title="DocuGenie - AI Document Intelligence",
    page_icon="📑",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern styling
st.markdown("""
<style>
    /* Global styles */
    .main {
        padding: 0;
    }
    
    /* Header styling */
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 50%, #f093fb 100%);
        padding: 3rem 2rem;
        border-radius: 20px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: url('data:image/svg+xml,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><defs><pattern id="grain" width="100" height="100" patternUnits="userSpaceOnUse"><circle cx="25" cy="25" r="1" fill="white" opacity="0.1"/><circle cx="75" cy="75" r="1" fill="white" opacity="0.1"/><circle cx="50" cy="10" r="0.5" fill="white" opacity="0.1"/></pattern></defs><rect width="100" height="100" fill="url(%23grain)"/></svg>');
        opacity: 0.3;
    }
    
    .main-header h1 {
        font-size: 3rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .main-header h3 {
        font-size: 1.5rem;
        font-weight: 400;
        margin-bottom: 1rem;
        opacity: 0.9;
    }
    
    .main-header p {
        font-size: 1rem;
        opacity: 0.8;
        margin: 0;
    }
    
    /* Feature cards */
    .feature-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #e9ecef;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .feature-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        width: 4px;
        height: 100%;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    .feature-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 25px rgba(0,0,0,0.15);
    }
    
    .feature-card h4 {
        color: #2c3e50;
        font-weight: 600;
        margin-bottom: 1rem;
        font-size: 1.3rem;
    }
    
    .feature-card p {
        color: #6c757d;
        line-height: 1.6;
        margin: 0;
    }
    
    /* Metric cards */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        text-align: center;
        border: 1px solid #e9ecef;
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 0.75rem 2rem;
        font-weight: 600;
        font-size: 1rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    .stButton > button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    
    /* Sidebar styling */
    .css-1d391kg {
        background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    }
    
    /* File uploader styling */
    .stFileUploader > div {
        border: 2px dashed #667eea;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        background: rgba(102, 126, 234, 0.05);
        transition: all 0.3s ease;
    }
    
    .stFileUploader > div:hover {
        border-color: #764ba2;
        background: rgba(102, 126, 234, 0.1);
    }
    
    /* Success/Error messages */
    .stAlert {
        border-radius: 10px;
        border: none;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    
    /* Tabs styling */
    .stTabs > div > div > div > div {
        background: transparent;
    }
    
    .stTabs > div > div > div > div > div {
        background: white;
        border-radius: 10px 10px 0 0;
        border: 1px solid #e9ecef;
        border-bottom: none;
        padding: 0.5rem 1rem;
        margin-right: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stTabs > div > div > div > div > div:hover {
        background: #f8f9fa;
    }
    
    /* Chat interface */
    .chat-message {
        background: #f8f9fa;
        padding: 1rem;
        border-radius: 10px;
        margin: 0.5rem 0;
        border-left: 4px solid #667eea;
    }
    
    .chat-question {
        background: #e3f2fd;
        border-left-color: #2196f3;
    }
    
    .chat-answer {
        background: #f3e5f5;
        border-left-color: #9c27b0;
    }
    
    /* Responsive design */
    @media (max-width: 768px) {
        .main-header h1 {
            font-size: 2rem;
        }
        
        .main-header h3 {
            font-size: 1.2rem;
        }
        
        .feature-card {
            padding: 1.5rem;
        }
    }
</style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables."""
    if 'document_processed' not in st.session_state:
        st.session_state.document_processed = False
    if 'analysis_results' not in st.session_state:
        st.session_state.analysis_results = None
    if 'document_text' not in st.session_state:
        st.session_state.document_text = None
    if 'document_images' not in st.session_state:
        st.session_state.document_images = []
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    if 'processing_status' not in st.session_state:
        st.session_state.processing_status = "idle"

def main_header():
    """Display the main header with gradient background."""
    st.markdown("""
    <div class="main-header">
        <h1>📑 DocuGenie</h1>
        <h3>Multi-Modal AI Agent for Smart Document Analysis</h3>
        <p>Powered by Gemini 2.5 Pro • Computer Vision • NLP • LLM Agents</p>
    </div>
    """, unsafe_allow_html=True)

def sidebar_upload():
    """Handle document upload in sidebar."""
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h3 style="color: #2c3e50; margin-bottom: 1rem;">📁 Document Upload</h3>
        </div>
        """, unsafe_allow_html=True)
        
        # File uploader
        uploaded_file = st.file_uploader(
            "Choose a document to analyze",
            type=['pdf', 'png', 'jpg', 'jpeg', 'tiff', 'bmp'],
            help="Support for PDF documents and image files"
        )
        
        if uploaded_file:
            st.success(f"✅ **{uploaded_file.name}** uploaded successfully!")
            
            # File info with better styling
            file_size = len(uploaded_file.getvalue()) / 1024  # KB
            st.info(f"""
            📊 **File Information:**
            - **Size:** {file_size:.1f} KB
            - **Type:** {uploaded_file.type or 'Unknown'}
            """)
            
            # Process button
            if st.button("🚀 Process Document", type="primary", use_container_width=True):
                return uploaded_file
        
        # Demo documents section
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h4 style="color: #2c3e50; margin-bottom: 1rem;">🎯 Try Demo Documents</h4>
        </div>
        """, unsafe_allow_html=True)
        
        demo_options = {
            "Sample Invoice": "demo/invoice_sample.pdf",
            "Sample Contract": "demo/contract_sample.pdf",
            "Sample Resume": "demo/resume_sample.pdf"
        }
        
        selected_demo = st.selectbox("Choose a demo document:", list(demo_options.keys()))
        if st.button("📋 Load Demo", use_container_width=True):
            st.info("Demo documents would be loaded here")
    
    return None

def display_features():
    """Display feature cards."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h4>🔍 Document Understanding</h4>
            <p>Advanced OCR + Computer Vision for text, tables, and visual elements</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h4>🧠 AI Analysis</h4>
            <p>Gemini 2.5 Pro powered entity extraction and intelligent summarization</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <h4>💬 Interactive Q&A</h4>
            <p>Ask natural language questions and get precise, contextual answers</p>
        </div>
        """, unsafe_allow_html=True)

def process_document(uploaded_file):
    """Process the uploaded document."""
    try:
        st.session_state.processing_status = "processing"
        
        # Initialize processors
        doc_processor = DocumentProcessor()
        gemini_analyzer = GeminiAnalyzer()
        
        # Process document
        with st.spinner("🔄 Processing document..."):
            # Extract text and images
            text, images = doc_processor.extract_content(uploaded_file)
            st.session_state.document_text = text
            st.session_state.document_images = images
            
            # Analyze with Gemini
            analysis = gemini_analyzer.analyze_document(text, images)
            st.session_state.analysis_results = analysis
            st.session_state.document_processed = True
        
        st.session_state.processing_status = "completed"
        st.success("✅ Document processed successfully!")
        
    except Exception as e:
        st.error(f"❌ Error processing document: {str(e)}")
        logger.error(f"Document processing error: {e}")
        st.session_state.processing_status = "error"

def display_analysis_results():
    """Display the analysis results."""
    if not st.session_state.analysis_results:
        return
    
    analysis = st.session_state.analysis_results
    
    # Main analysis section
    st.header("📊 Document Analysis Results")
    
    # Summary
    if 'summary' in analysis:
        st.subheader("📝 Executive Summary")
        st.markdown(analysis['summary'])
    
    # Key entities
    if 'entities' in analysis:
        st.subheader("🔍 Key Entities Extracted")
        
        # Create a DataFrame for better display
        entities_df = pd.DataFrame(analysis['entities'])
        if not entities_df.empty:
            st.dataframe(entities_df, use_container_width=True)
    
    # Document type and confidence
    if 'document_type' in analysis:
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Document Type", analysis['document_type'])
        with col2:
            st.metric("Confidence Score", f"{analysis.get('confidence', 0):.1%}")
        with col3:
            st.metric("Processing Time", f"{analysis.get('processing_time', 0):.2f}s")

def chat_interface():
    """Interactive chat interface for document Q&A."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #2c3e50; margin-bottom: 1rem;">💬 Ask Questions About Your Document</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.document_processed:
        st.info("📄 Please upload and process a document first to start asking questions.")
        return
    
    # Chat input with better styling
    st.markdown("### 🤔 Ask a Question")
    user_question = st.text_input(
        "Ask anything about your document:",
        placeholder="e.g., What's the total amount? Who are the parties involved? What are the key terms?",
        help="Type your question here and click Ask to get an AI-powered answer"
    )
    
    col1, col2 = st.columns([1, 4])
    with col1:
        ask_button = st.button("🔍 Ask", type="primary", use_container_width=True)
    
    # Process question
    if ask_button and user_question:
        try:
            gemini_analyzer = GeminiAnalyzer()
            
            with st.spinner("🤔 Thinking..."):
                answer = gemini_analyzer.answer_question(
                    user_question, 
                    st.session_state.document_text, 
                    st.session_state.document_images
                )
            
            # Add to chat history
            st.session_state.chat_history.append({
                'question': user_question,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            })
            
            # Display answer with better styling
            st.markdown("### 💡 Answer")
            st.markdown(f"""
            <div class="chat-answer" style="padding: 1.5rem; border-radius: 10px; background: #f3e5f5; border-left: 4px solid #9c27b0;">
                {answer}
            </div>
            """, unsafe_allow_html=True)
            
        except Exception as e:
            st.error(f"❌ Error getting answer: {str(e)}")
    
    # Chat history with better styling
    if st.session_state.chat_history:
        st.markdown("### 📚 Chat History")
        for i, chat in enumerate(reversed(st.session_state.chat_history[-5:])):  # Show last 5
            with st.expander(f"💬 Q: {chat['question'][:50]}...", expanded=False):
                st.markdown(f"""
                <div class="chat-question" style="padding: 1rem; border-radius: 8px; background: #e3f2fd; border-left: 4px solid #2196f3; margin-bottom: 1rem;">
                    <strong>Question:</strong> {chat['question']}
                </div>
                <div class="chat-answer" style="padding: 1rem; border-radius: 8px; background: #f3e5f5; border-left: 4px solid #9c27b0;">
                    <strong>Answer:</strong> {chat['answer']}
                </div>
                """, unsafe_allow_html=True)
                st.caption(f"⏰ Asked at: {chat['timestamp']}")

def export_section():
    """Export functionality."""
    st.markdown("""
    <div style="text-align: center; padding: 1rem 0;">
        <h2 style="color: #2c3e50; margin-bottom: 1rem;">📤 Export Results</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state.analysis_results:
        st.info("📄 Process a document first to export results.")
        return
    
    st.markdown("### 📋 Choose Export Format")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; border: 1px solid #e9ecef;">
            <h4>📄 JSON Format</h4>
            <p style="color: #6c757d; font-size: 0.9rem;">Machine-readable data for API integration</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📄 Export as JSON", use_container_width=True):
            json_data = json.dumps(st.session_state.analysis_results, indent=2)
            st.download_button(
                label="Download JSON",
                data=json_data,
                file_name=f"docugenie_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; border: 1px solid #e9ecef;">
            <h4>📊 Excel Format</h4>
            <p style="color: #6c757d; font-size: 0.9rem;">Spreadsheet format for data analysis</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📊 Export as Excel", use_container_width=True):
            # Convert analysis to Excel format
            df = pd.DataFrame(st.session_state.analysis_results.get('entities', []))
            if not df.empty:
                excel_data = df.to_excel(index=False)
                st.download_button(
                    label="Download Excel",
                    data=excel_data,
                    file_name=f"docugenie_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
    
    with col3:
        st.markdown("""
        <div style="text-align: center; padding: 1rem; background: #f8f9fa; border-radius: 10px; border: 1px solid #e9ecef;">
            <h4>📝 Text Report</h4>
            <p style="color: #6c757d; font-size: 0.9rem;">Human-readable summary report</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("📝 Export as Report", use_container_width=True):
            # Generate a formatted report
            report = generate_report(st.session_state.analysis_results)
            st.download_button(
                label="Download Report",
                data=report,
                file_name=f"docugenie_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain",
                use_container_width=True
            )

def display_detailed_analysis(analysis: Dict[str, Any]):
    """Display detailed analysis in a readable text format."""
    
    # Document Overview
    st.markdown("### 📋 Document Overview")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"**Document Type:** {analysis.get('document_type', 'Unknown')}")
    with col2:
        st.info(f"**Confidence:** {analysis.get('confidence', 0):.1%}")
    with col3:
        st.info(f"**Processing Time:** {analysis.get('processing_time', 0):.2f}s")
    
    # Executive Summary
    if 'summary' in analysis and analysis['summary']:
        st.markdown("### 📝 Executive Summary")
        st.markdown(analysis['summary'])
    
    # Key Entities
    if 'entities' in analysis and analysis['entities']:
        st.markdown("### 🔍 Key Entities Extracted")
        entities_df = pd.DataFrame(analysis['entities'])
        if not entities_df.empty:
            st.dataframe(entities_df, use_container_width=True)
    
    # Key Points
    if 'key_points' in analysis and analysis['key_points']:
        st.markdown("### 🎯 Key Points")
        for i, point in enumerate(analysis['key_points'], 1):
            st.markdown(f"{i}. {point}")
    
    # Risk Factors
    if 'risk_factors' in analysis and analysis['risk_factors']:
        st.markdown("### ⚠️ Risk Factors")
        for i, risk in enumerate(analysis['risk_factors'], 1):
            st.markdown(f"{i}. {risk}")
    
    # Sentiment Analysis
    if 'sentiment' in analysis and analysis['sentiment']:
        st.markdown("### 😊 Sentiment Analysis")
        st.markdown(analysis['sentiment'])
    
    # Document Classification
    if 'classification' in analysis and analysis['classification']:
        st.markdown("### 🏷️ Document Classification")
        st.markdown(analysis['classification'])
    
    # Raw Analysis Data (collapsible)
    with st.expander("🔧 Raw Analysis Data (JSON)"):
        st.json(analysis)

def generate_report(analysis: Dict[str, Any]) -> str:
    """Generate a formatted text report."""
    report = f"""
DOCUGENIE ANALYSIS REPORT
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*50}

DOCUMENT TYPE: {analysis.get('document_type', 'Unknown')}
CONFIDENCE: {analysis.get('confidence', 0):.1%}

EXECUTIVE SUMMARY:
{analysis.get('summary', 'No summary available')}

KEY ENTITIES:
"""
    
    for entity in analysis.get('entities', []):
        report += f"- {entity.get('type', 'Unknown')}: {entity.get('value', 'N/A')}\n"
    
    # Add key points if available
    if 'key_points' in analysis and analysis['key_points']:
        report += "\nKEY POINTS:\n"
        for i, point in enumerate(analysis['key_points'], 1):
            report += f"{i}. {point}\n"
    
    # Add risk factors if available
    if 'risk_factors' in analysis and analysis['risk_factors']:
        report += "\nRISK FACTORS:\n"
        for i, risk in enumerate(analysis['risk_factors'], 1):
            report += f"{i}. {risk}\n"
    
    return report

def main():
    """Main application function."""
    # Initialize session state
    initialize_session_state()
    
    # Display header
    main_header()
    
    # Sidebar upload
    uploaded_file = sidebar_upload()
    
    # Process document if uploaded
    if uploaded_file:
        process_document(uploaded_file)
    
    # Main content area
    if not st.session_state.document_processed:
        # Landing page
        st.markdown("## 🚀 Welcome to DocuGenie")
        st.markdown("""
        DocuGenie is your AI-powered document intelligence assistant. Upload any document and get instant insights, 
        summaries, and answers to your questions using the power of Gemini 2.5 Pro.
        """)
        
        display_features()
        
        # Usage instructions
        st.markdown("## 📋 How to Use")
        st.markdown("""
        1. **Upload** - Use the sidebar to upload your document (PDF, images supported)
        2. **Process** - Click the process button to analyze your document
        3. **Explore** - View extracted entities, summaries, and insights
        4. **Ask** - Use the chat interface to ask questions about your document
        5. **Export** - Download results in JSON, Excel, or report format
        """)
        
    else:
        # Document has been processed
        display_analysis_results()
        
        # Tabs for different features
        tab1, tab2, tab3 = st.tabs(["💬 Q&A Chat", "📊 Detailed Analysis", "📤 Export"])
        
        with tab1:
            chat_interface()
        
        with tab2:
            st.subheader("🔍 Detailed Document Analysis")
            if st.session_state.analysis_results:
                display_detailed_analysis(st.session_state.analysis_results)
        
        with tab3:
            export_section()

if __name__ == "__main__":
    main()