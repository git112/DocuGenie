# 📑 DocuGenie: Multi-Modal AI Agent for Smart Document Analysis

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.48+-red.svg)](https://streamlit.io)
[![Gemini](https://img.shields.io/badge/Gemini-2.5%20Pro-orange.svg)](https://ai.google.dev/gemini)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

**DocuGenie** is an AI-powered multi-modal document intelligence system that combines Computer Vision (CV), Natural Language Processing (NLP), and Large Language Models (LLMs) to automatically analyze, summarize, and answer questions from unstructured documents such as contracts, invoices, resumes, and research papers.

## ✨ Core Features

### 🔍 Document Understanding (CV + OCR)
- **Multi-format Support**: Handles PDFs, images (PNG, JPG, TIFF, BMP)
- **Advanced OCR**: Tesseract-powered text extraction with image preprocessing
- **Layout Analysis**: Detects tables, sections, and visual elements
- **Image Processing**: OpenCV-based enhancement for better OCR results

### 🧠 AI Analysis with Gemini 2.5 Pro
- **Entity Extraction**: Identifies names, dates, amounts, organizations, and more
- **Document Classification**: Automatically categorizes documents (invoice, contract, resume, etc.)
- **Intelligent Summarization**: Creates concise, actionable summaries
- **Risk Assessment**: Identifies potential issues and concerns
- **Sentiment Analysis**: Evaluates document tone and urgency

### 💬 Interactive Q&A
- **Natural Language Queries**: Ask questions in plain English
- **Contextual Answers**: Precise responses backed by document content
- **Chat History**: Track conversation history for reference
- **Multi-turn Conversations**: Follow-up questions and clarifications

### 🔄 Agentic Self-Correction
- **Confidence Scoring**: AI validates its own analysis quality
- **Fallback Mechanisms**: Graceful handling of parsing errors
- **Quality Assurance**: Multiple validation layers for accuracy

### 📊 Export & Reports
- **Multiple Formats**: JSON, Excel, PDF, and text reports
- **Structured Data**: Clean, machine-readable output
- **Custom Templates**: Configurable report formats
- **Batch Processing**: Handle multiple documents efficiently

## 🛠️ Tech Stack

### Core AI Modules
- **OCR/CV**: OpenCV, Tesseract, PyMuPDF
- **NLP**: Google Gemini 2.5 Pro, LangChain integration
- **Document Processing**: PyMuPDF, Pillow, pdf2image

### Application Layer
- **Backend**: Python 3.8+, Streamlit
- **Frontend**: Streamlit (responsive web interface)
- **Data Processing**: Pandas, NumPy, Pydantic

### Deployment Ready
- **Containerization**: Docker support
- **Cloud Deployment**: Hugging Face Spaces, Render, AWS, GCP
- **Monitoring**: Built-in logging and error tracking

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/your-username/docugenie.git
cd docugenie
```

### 2. Set Up Environment
```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure API Keys
```bash
# Copy environment template
cp env_example.txt .env

# Edit .env file with your API keys
# Required: GOOGLE_API_KEY
# Optional: OPENAI_API_KEY
```

### 4. Run the Application
```bash
streamlit run app.py
```

The application will be available at `http://localhost:8501`

## 📋 How to Use

### 1. Upload Document
- Use the sidebar to upload your document
- Supported formats: PDF, PNG, JPG, JPEG, TIFF, BMP
- Maximum file size: 50MB

### 2. Process Document
- Click "Process Document" to analyze
- View real-time processing status
- Get instant insights and entity extraction

### 3. Explore Results
- **Summary**: Executive overview of the document
- **Entities**: Extracted key information
- **Key Points**: Important findings and insights
- **Risk Factors**: Potential concerns identified

### 4. Ask Questions
- Use natural language to query the document
- Examples:
  - "What's the total invoice amount?"
  - "Who are the parties in this contract?"
  - "What are the key terms and conditions?"
  - "Summarize the termination clause"

### 5. Export Results
- Download analysis in multiple formats
- JSON for API integration
- Excel for spreadsheet analysis
- PDF reports for sharing

## 📊 Example Use Cases

### Legal & Compliance
- **Contract Analysis**: Extract clauses, obligations, and key terms
- **Risk Assessment**: Identify potential legal issues
- **Due Diligence**: Rapid document review and summarization

### Finance & Accounting
- **Invoice Processing**: Extract amounts, dates, and vendor information
- **Financial Reports**: Analyze statements and identify trends
- **Expense Management**: Automated receipt processing

### Human Resources
- **Resume Screening**: Extract skills, experience, and qualifications
- **Job Applications**: Automated candidate evaluation
- **Performance Reviews**: Analyze feedback and identify patterns

### Research & Academia
- **Paper Summarization**: Extract key findings and methodologies
- **Literature Review**: Compare multiple research documents
- **Data Extraction**: Convert unstructured research into structured data

## 🏗️ Project Structure

```
docugenie/
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
├── env_example.txt        # Environment configuration template
├── README.md             # Project documentation
├── src/                  # Source code modules
│   ├── __init__.py
│   ├── config.py         # Configuration management
│   ├── utils.py          # Utility functions
│   ├── document_processor.py  # Document processing & OCR
│   └── gemini_analyzer.py     # Gemini AI integration
├── demo/                 # Demo documents
├── tests/                # Test suite
└── docs/                 # Documentation
```

## 🔧 Configuration

### Environment Variables
```bash
# Required
GOOGLE_API_KEY=your_gemini_api_key

# Optional
OPENAI_API_KEY=your_openai_api_key
DEBUG=False
LOG_LEVEL=INFO
CACHE_ENABLED=True
MAX_FILE_SIZE_MB=50
```

### Customization
- Modify `src/config.py` for application settings
- Adjust OCR parameters in `src/document_processor.py`
- Customize Gemini prompts in `src/gemini_analyzer.py`

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Run with coverage
pytest --cov=src tests/

# Run specific test
pytest tests/test_document_processor.py
```

## 🚀 Deployment

### Local Development
```bash
streamlit run app.py --server.port 8501
```

### Docker Deployment
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Cloud Deployment
- **Hugging Face Spaces**: One-click deployment
- **Render**: Automatic deployment from GitHub
- **AWS/GCP**: Container-based deployment

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/your-username/docugenie.git

# Create feature branch
git checkout -b feature/amazing-feature

# Make changes and test
pytest tests/

# Commit and push
git commit -m "Add amazing feature"
git push origin feature/amazing-feature

# Create Pull Request
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Google Gemini**: For providing the powerful AI model
- **Streamlit**: For the excellent web framework
- **OpenCV & Tesseract**: For computer vision and OCR capabilities
- **PyMuPDF**: For PDF processing capabilities

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/your-username/docugenie/issues)
- **Discussions**: [GitHub Discussions](https://github.com/your-username/docugenie/discussions)
- **Email**: support@docugenie.ai

## 🔮 Roadmap

- [ ] Multi-language support (English, Spanish, French, etc.)
- [ ] Google Drive & OneDrive integration
- [ ] Real-time collaboration features
- [ ] Advanced document comparison
- [ ] Custom model fine-tuning
- [ ] Chrome extension
- [ ] Mobile app
- [ ] Enterprise features (SSO, audit logs, etc.)

---

**Made with ❤️ by Naseta**

*Transform your documents into actionable intelligence with the power of AI.*
