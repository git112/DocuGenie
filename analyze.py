"""
Legacy compatibility module for DocuMind.
This module provides backward compatibility with the original analyze.py functions.
"""

import os
from src.gemini_analyzer import GeminiAnalyzer
from src.config import Config

# Initialize configuration and analyzer
config = Config()
gemini_analyzer = GeminiAnalyzer(config)

def analyze_document_with_gemini(text=None, image=None):
    """
    Legacy function for document analysis.
    
    Args:
        text: Document text content
        image: PIL Image object
        
    Returns:
        Analysis results as formatted text
    """
    try:
        # Convert single image to list for compatibility
        images = [image] if image else None
        
        # Perform analysis using the new analyzer
        analysis_results = gemini_analyzer.analyze_document(text, images)
        
        # Format results for backward compatibility
        if analysis_results.get("error"):
            return f"An error occurred: {analysis_results['error']}"
        
        # Create formatted output
        output = []
        
        if analysis_results.get("document_type"):
            output.append(f"**Document Type:** {analysis_results['document_type']}")
        
        if analysis_results.get("summary"):
            output.append(f"\n**Summary:**\n{analysis_results['summary']}")
        
        if analysis_results.get("entities"):
            output.append("\n**Key Entities:**")
            for entity in analysis_results["entities"]:
                output.append(f"- {entity.get('type', 'Unknown')}: {entity.get('value', 'N/A')}")
        
        if analysis_results.get("key_points"):
            output.append("\n**Key Points:**")
            for point in analysis_results["key_points"]:
                output.append(f"- {point}")
        
        if analysis_results.get("confidence"):
            output.append(f"\n**Confidence Score:** {analysis_results['confidence']:.1%}")
        
        return "\n".join(output)
        
    except Exception as e:
        return f"An error occurred: {e}"

def answer_user_question(user_question, text=None, image=None):
    """
    Legacy function for answering questions about documents.
    
    Args:
        user_question: The question to answer
        text: Document text content
        image: PIL Image object
        
    Returns:
        Answer to the question
    """
    try:
        # Convert single image to list for compatibility
        images = [image] if image else None
        
        # Get answer using the new analyzer
        answer = gemini_analyzer.answer_question(user_question, text, images)
        
        return answer
        
    except Exception as e:
        return f"An error occurred: {e}"

# Backward compatibility aliases
def analyze_document(text=None, image=None):
    """Alias for analyze_document_with_gemini for backward compatibility."""
    return analyze_document_with_gemini(text, image)

def ask_question(question, text=None, image=None):
    """Alias for answer_user_question for backward compatibility."""
    return answer_user_question(question, text, image)