"""
Document processing module for extracting text and images from various file formats.
"""

import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import cv2
import numpy as np
from typing import Tuple, List, Optional, Union
import io
import logging
from .config import Config
from .utils import validate_file_upload, format_file_size

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Handles document processing and text extraction."""
    
    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self.supported_formats = self.config.supported_formats
        
    def extract_content(self, uploaded_file) -> Tuple[Optional[str], List[Image.Image]]:
        """
        Extract text and images from uploaded file.
        
        Args:
            uploaded_file: Streamlit uploaded file object
            
        Returns:
            Tuple of (text, images)
        """
        try:
            # Validate file
            is_valid, message = validate_file_upload(uploaded_file)
            if not is_valid:
                raise ValueError(message)
            
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                return self._process_pdf(uploaded_file)
            else:
                return self._process_image(uploaded_file)
                
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            raise
    
    def _process_pdf(self, uploaded_file) -> Tuple[str, List[Image.Image]]:
        """Process PDF file and extract text and images."""
        try:
            # Read PDF
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            text_content = []
            images = []
            
            for page_num in range(len(pdf_document)):
                page = pdf_document.load_page(page_num)
                
                # Extract text
                page_text = page.get_text()
                if page_text.strip():
                    text_content.append(page_text)
                
                # Extract images
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        pix = fitz.Pixmap(pdf_document, xref)
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            pil_image = Image.open(io.BytesIO(img_data))
                            images.append(pil_image)
                        pix = None
                    except Exception as e:
                        logger.warning(f"Failed to extract image {img_index} from page {page_num}: {e}")
            
            pdf_document.close()
            
            # Combine all text
            full_text = "\n\n".join(text_content)
            
            # If no text found, try OCR on images
            if not full_text.strip() and images:
                logger.info("No text found in PDF, attempting OCR on extracted images")
                ocr_text = self._perform_ocr_on_images(images)
                full_text = ocr_text
            
            return full_text, images
            
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            raise
    
    def _process_image(self, uploaded_file) -> Tuple[Optional[str], List[Image.Image]]:
        """Process image file and extract text using OCR."""
        try:
            # Open image
            image = Image.open(uploaded_file)
            images = [image]
            
            # Perform OCR
            text = self._perform_ocr_on_images(images)
            
            return text, images
            
        except Exception as e:
            logger.error(f"Error processing image: {e}")
            raise
    
    def _perform_ocr_on_images(self, images: List[Image.Image]) -> str:
        """Perform OCR on a list of images."""
        try:
            ocr_results = []
            
            for i, image in enumerate(images):
                # Convert PIL image to OpenCV format
                opencv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
                
                # Preprocess image for better OCR
                processed_image = self._preprocess_image_for_ocr(opencv_image)
                
                # Perform OCR
                try:
                    # Try with default configuration
                    text = pytesseract.image_to_string(processed_image)
                    
                    # If no text found, try with different configurations
                    if not text.strip():
                        text = pytesseract.image_to_string(
                            processed_image, 
                            config='--psm 6 --oem 3'
                        )
                    
                    if text.strip():
                        ocr_results.append(text.strip())
                        
                except Exception as e:
                    logger.warning(f"OCR failed for image {i}: {e}")
                    continue
            
            return "\n\n".join(ocr_results)
            
        except Exception as e:
            logger.error(f"Error in OCR processing: {e}")
            return ""
    
    def _preprocess_image_for_ocr(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results."""
        try:
            # Convert to grayscale
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image
            
            # Apply noise reduction
            denoised = cv2.medianBlur(gray, 3)
            
            # Apply thresholding
            _, thresh = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            
            # Apply morphological operations
            kernel = np.ones((1, 1), np.uint8)
            processed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
            
            return processed
            
        except Exception as e:
            logger.warning(f"Image preprocessing failed: {e}")
            return image
    
    def extract_metadata(self, uploaded_file) -> dict:
        """Extract metadata from uploaded file."""
        try:
            metadata = {
                "filename": uploaded_file.name,
                "file_size": format_file_size(len(uploaded_file.getvalue())),
                "file_type": uploaded_file.type,
                "upload_time": uploaded_file.upload_time.isoformat() if hasattr(uploaded_file, 'upload_time') else None
            }
            
            # Add format-specific metadata
            file_extension = uploaded_file.name.lower().split('.')[-1]
            
            if file_extension == 'pdf':
                pdf_metadata = self._extract_pdf_metadata(uploaded_file)
                metadata.update(pdf_metadata)
            elif file_extension in ['png', 'jpg', 'jpeg', 'tiff', 'bmp']:
                image_metadata = self._extract_image_metadata(uploaded_file)
                metadata.update(image_metadata)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {e}")
            return {"error": str(e)}
    
    def _extract_pdf_metadata(self, uploaded_file) -> dict:
        """Extract metadata from PDF file."""
        try:
            pdf_document = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            
            metadata = {
                "page_count": len(pdf_document),
                "title": pdf_document.metadata.get("title", ""),
                "author": pdf_document.metadata.get("author", ""),
                "subject": pdf_document.metadata.get("subject", ""),
                "creator": pdf_document.metadata.get("creator", ""),
                "producer": pdf_document.metadata.get("producer", ""),
                "creation_date": pdf_document.metadata.get("creationDate", ""),
                "modification_date": pdf_document.metadata.get("modDate", "")
            }
            
            pdf_document.close()
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting PDF metadata: {e}")
            return {}
    
    def _extract_image_metadata(self, uploaded_file) -> dict:
        """Extract metadata from image file."""
        try:
            image = Image.open(uploaded_file)
            
            metadata = {
                "width": image.width,
                "height": image.height,
                "mode": image.mode,
                "format": image.format,
                "dpi": image.info.get("dpi", (None, None))
            }
            
            # Extract EXIF data if available
            if hasattr(image, '_getexif') and image._getexif():
                exif = image._getexif()
                if exif:
                    metadata["exif"] = {
                        "make": exif.get(271, ""),
                        "model": exif.get(272, ""),
                        "date_time": exif.get(36867, "")
                    }
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting image metadata: {e}")
            return {}
