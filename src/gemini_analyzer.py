"""
Gemini 2.5 Pro powered document analyzer for intelligent document processing.
"""

import google.generativeai as genai
from PIL import Image
import time
import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

from .config import Config
from .utils import extract_text_safely, format_duration

logger = logging.getLogger(__name__)

class GeminiAnalyzer:
    """Gemini 2.5 Pro powered document analyzer."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.config.validate_config()
        
        # Configure Gemini
        genai.configure(api_key=self.config.google_api_key)
        self.model = genai.GenerativeModel(
            model_name=self.config.gemini_model,
            generation_config={
                "temperature": self.config.gemini_temperature,
                "max_output_tokens": self.config.gemini_max_tokens,
            }
        )
        
        # Safety settings
        self.safety_settings = [
            {
                "category": "HARM_CATEGORY_HARASSMENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_HATE_SPEECH",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            },
            {
                "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
                "threshold": "BLOCK_MEDIUM_AND_ABOVE"
            }
        ]
    
    def analyze_document(self, text: Optional[str] = None, images: Optional[List[Image.Image]] = None) -> Dict[str, Any]:
        """
        Perform comprehensive document analysis using Gemini 2.5 Pro.
        
        Args:
            text: Extracted text from document
            images: List of images from document
            
        Returns:
            Dictionary containing analysis results
        """
        start_time = time.time()
        
        try:
            # Prepare content for analysis
            content_parts = self._prepare_content_for_analysis(text, images)
            
            # Create analysis prompt
            analysis_prompt = self._create_analysis_prompt()
            
            # Perform analysis
            response = self._generate_response(analysis_prompt, content_parts)
            
            # Parse and structure results
            analysis_results = self._parse_analysis_response(response)
            
            # Add metadata
            processing_time = time.time() - start_time
            analysis_results.update({
                "processing_time": processing_time,
                "timestamp": datetime.now().isoformat(),
                "model_used": self.config.gemini_model,
                "confidence": self._calculate_confidence(analysis_results)
            })
            
            logger.info(f"Document analysis completed in {format_duration(processing_time)}")
            return analysis_results
            
        except Exception as e:
            logger.error(f"Error in document analysis: {e}")
            return {
                "error": str(e),
                "processing_time": time.time() - start_time,
                "timestamp": datetime.now().isoformat()
            }
    
    def answer_question(self, question: str, text: Optional[str] = None, images: Optional[List[Image.Image]] = None) -> str:
        """
        Answer specific questions about the document.
        
        Args:
            question: User's question
            text: Document text
            images: Document images
            
        Returns:
            Answer to the question
        """
        try:
            # Prepare content
            content_parts = self._prepare_content_for_analysis(text, images)
            
            # Create Q&A prompt
            qa_prompt = self._create_qa_prompt(question)
            
            # Generate answer
            response = self._generate_response(qa_prompt, content_parts)
            
            return response.text
            
        except Exception as e:
            logger.error(f"Error answering question: {e}")
            return f"I apologize, but I encountered an error while processing your question: {str(e)}"
    
    def _prepare_content_for_analysis(self, text: Optional[str], images: Optional[List[Image.Image]]) -> List[Any]:
        """Prepare content for Gemini analysis."""
        content_parts = []
        
        # Add text content
        if text and text.strip():
            # Truncate text if too long
            safe_text = extract_text_safely(text, max_length=30000)
            content_parts.append(safe_text)
        
        # Add images
        if images:
            for i, image in enumerate(images[:5]):  # Limit to 5 images
                try:
                    # Resize image if too large
                    max_size = (1024, 1024)
                    if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                        image.thumbnail(max_size, Image.Resampling.LANCZOS)
                    
                    content_parts.append(image)
                except Exception as e:
                    logger.warning(f"Failed to process image {i}: {e}")
        
        return content_parts
    
    def _create_analysis_prompt(self) -> str:
        """Create comprehensive analysis prompt."""
        return """
        You are DocuGenie, an expert AI document analysis system powered by Gemini 2.5 Pro. 
        Your task is to analyze the provided document and extract comprehensive insights.
        
        Please provide a detailed analysis in the following JSON format:
        {
            "document_type": "invoice|contract|resume|report|letter|other",
            "summary": "A concise 2-3 sentence summary of the document's main purpose and content",
            "entities": [
                {
                    "type": "person|organization|date|amount|location|email|phone|url|other",
                    "value": "extracted value",
                    "confidence": 0.95,
                    "context": "brief context about where this entity was found"
                }
            ],
            "key_points": [
                "Important point 1",
                "Important point 2",
                "Important point 3"
            ],
            "risk_factors": [
                "Any potential risks or concerns identified"
            ],
            "recommendations": [
                "Actionable recommendations based on the analysis"
            ],
            "sentiment": "positive|neutral|negative",
            "urgency": "high|medium|low",
            "completeness": "complete|partial|incomplete"
        }
        
        Guidelines:
        1. Be precise and accurate in entity extraction
        2. Identify document type based on content and structure
        3. Extract all relevant entities (names, dates, amounts, organizations, etc.)
        4. Provide actionable insights and recommendations
        5. Assess document completeness and quality
        6. Identify any potential risks or issues
        
        For invoices: Focus on amounts, dates, vendor info, line items
        For contracts: Focus on parties, terms, dates, obligations, penalties
        For resumes: Focus on skills, experience, education, contact info
        For reports: Focus on findings, conclusions, recommendations
        
        Return only valid JSON without any additional text or explanations.
        """
    
    def _create_qa_prompt(self, question: str) -> str:
        """Create Q&A prompt."""
        return f"""
        You are DocuGenie, an expert document analysis assistant. 
        Based on the provided document content, please answer the following question accurately and concisely.
        
        Question: {question}
        
        Instructions:
        1. Answer based only on the information present in the document
        2. If the information is not available, clearly state that
        3. Provide specific quotes or references when possible
        4. Be concise but thorough
        5. If the question is ambiguous, ask for clarification
        6. Provide your answer in clear, readable text format (not JSON)
        
        Please provide a clear, direct answer to the question in natural language.
        """
    
    def _generate_response(self, prompt: str, content_parts: List[Any]) -> Any:
        """Generate response from Gemini model."""
        try:
            # Combine prompt with content
            full_content = [prompt] + content_parts
            
            # Generate response
            response = self.model.generate_content(
                full_content,
                safety_settings=self.safety_settings
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error generating Gemini response: {e}")
            raise
    
    def _parse_analysis_response(self, response: Any) -> Dict[str, Any]:
        """Parse and structure the analysis response."""
        try:
            # Extract text from response
            response_text = response.text.strip()
            
            # Try to parse as JSON
            try:
                analysis_data = json.loads(response_text)
                return analysis_data
            except json.JSONDecodeError:
                # If JSON parsing fails, create structured response from text
                return self._fallback_analysis_parsing(response_text)
                
        except Exception as e:
            logger.error(f"Error parsing analysis response: {e}")
            return {
                "document_type": "unknown",
                "summary": "Analysis failed due to parsing error",
                "entities": [],
                "error": str(e)
            }
    
    def _fallback_analysis_parsing(self, response_text: str) -> Dict[str, Any]:
        """Fallback parsing when JSON parsing fails."""
        return {
            "document_type": "unknown",
            "summary": response_text[:500] + "..." if len(response_text) > 500 else response_text,
            "entities": [],
            "key_points": [],
            "risk_factors": [],
            "recommendations": [],
            "sentiment": "neutral",
            "urgency": "medium",
            "completeness": "unknown",
            "raw_response": response_text
        }
    
    def _calculate_confidence(self, analysis_results: Dict[str, Any]) -> float:
        """Calculate confidence score for the analysis."""
        try:
            confidence_factors = []
            
            # Document type confidence
            if analysis_results.get("document_type") and analysis_results["document_type"] != "unknown":
                confidence_factors.append(0.3)
            
            # Entity extraction confidence
            entities = analysis_results.get("entities", [])
            if entities:
                avg_entity_confidence = sum(e.get("confidence", 0.5) for e in entities) / len(entities)
                confidence_factors.append(avg_entity_confidence * 0.4)
            
            # Summary quality confidence
            summary = analysis_results.get("summary", "")
            if summary and len(summary) > 50:
                confidence_factors.append(0.2)
            
            # Key points confidence
            key_points = analysis_results.get("key_points", [])
            if key_points:
                confidence_factors.append(0.1)
            
            return min(sum(confidence_factors), 1.0)
            
        except Exception as e:
            logger.warning(f"Error calculating confidence: {e}")
            return 0.5
    
    def extract_entities(self, text: str, entity_types: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """Extract specific entities from text."""
        try:
            if entity_types is None:
                entity_types = ["person", "organization", "date", "amount", "location", "email", "phone"]
            
            prompt = f"""
            Extract the following entity types from the text: {', '.join(entity_types)}
            
            Return the results in JSON format:
            [
                {{
                    "type": "entity_type",
                    "value": "extracted_value",
                    "confidence": 0.95,
                    "context": "brief context"
                }}
            ]
            
            Text to analyze:
            {text[:10000]}  # Limit text length
            """
            
            response = self._generate_response(prompt, [text])
            
            try:
                entities = json.loads(response.text)
                return entities if isinstance(entities, list) else []
            except json.JSONDecodeError:
                return []
                
        except Exception as e:
            logger.error(f"Error extracting entities: {e}")
            return []
    
    def summarize_text(self, text: str, max_length: int = 500) -> str:
        """Generate a concise summary of the text."""
        try:
            prompt = f"""
            Summarize the following text in {max_length} characters or less:
            
            {text[:15000]}  # Limit input text
            
            Provide a clear, concise summary that captures the main points.
            """
            
            response = self._generate_response(prompt, [text])
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"Error summarizing text: {e}")
            return "Summary generation failed."
