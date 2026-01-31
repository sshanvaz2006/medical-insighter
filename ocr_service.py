"""
OCR Service
Handles Optical Character Recognition for medical documents
Using EasyOCR for accurate text extraction
"""

import easyocr
from PIL import Image
import pdf2image
import numpy as np
from typing import List, Dict, Tuple
import os
import tempfile
from app.config import get_settings
import time

settings = get_settings()


class OCRService:
    """OCR Service using EasyOCR"""
    
    def __init__(self):
        """Initialize OCR reader"""
        self.reader = easyocr.Reader(
            settings.OCR_LANGUAGES,
            gpu=settings.OCR_GPU
        )
    
    def extract_text_from_image(self, image_path: str) -> Dict:
        """
        Extract text from an image file
        
        Returns:
            dict: {
                'text': str,
                'confidence': float,
                'details': list of detected text blocks
            }
        """
        start_time = time.time()
        
        try:
            # Read image
            image = Image.open(image_path)
            
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Perform OCR
            results = self.reader.readtext(np.array(image), paragraph=True)
            
            # Extract text and confidence
            text_blocks = []
            all_text = []
            total_confidence = 0
            
            for detection in results:
                bbox, text, confidence = detection
                text_blocks.append({
                    'text': text,
                    'confidence': confidence,
                    'bbox': bbox
                })
                all_text.append(text)
                total_confidence += confidence
            
            # Calculate average confidence
            avg_confidence = total_confidence / len(results) if results else 0
            
            processing_time = time.time() - start_time
            
            return {
                'text': '\n'.join(all_text),
                'confidence': avg_confidence,
                'details': text_blocks,
                'processing_time': processing_time,
                'success': True
            }
        
        except Exception as e:
            return {
                'text': '',
                'confidence': 0,
                'details': [],
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    def extract_text_from_pdf(self, pdf_path: str) -> Dict:
        """
        Extract text from a PDF file
        
        Returns:
            dict: {
                'text': str,
                'confidence': float,
                'pages': int,
                'page_results': list of page results
            }
        """
        start_time = time.time()
        
        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(pdf_path, dpi=300)
            
            page_results = []
            all_text = []
            total_confidence = 0
            
            for page_num, image in enumerate(images, 1):
                # Save temp image
                with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
                    image.save(tmp.name, 'JPEG')
                    tmp_path = tmp.name
                
                # Extract text from page
                page_result = self.extract_text_from_image(tmp_path)
                page_result['page_number'] = page_num
                page_results.append(page_result)
                
                all_text.append(f"--- Page {page_num} ---\n{page_result['text']}")
                total_confidence += page_result['confidence']
                
                # Clean up temp file
                os.unlink(tmp_path)
            
            # Calculate average confidence
            avg_confidence = total_confidence / len(images) if images else 0
            
            processing_time = time.time() - start_time
            
            return {
                'text': '\n\n'.join(all_text),
                'confidence': avg_confidence,
                'pages': len(images),
                'page_results': page_results,
                'processing_time': processing_time,
                'success': True
            }
        
        except Exception as e:
            return {
                'text': '',
                'confidence': 0,
                'pages': 0,
                'page_results': [],
                'processing_time': time.time() - start_time,
                'success': False,
                'error': str(e)
            }
    
    def process_document(self, file_path: str, file_type: str) -> Dict:
        """
        Process a document (image or PDF) and extract text
        
        Args:
            file_path: Path to the document
            file_type: File extension (pdf, jpg, jpeg, png, tiff)
        
        Returns:
            dict: OCR results with text and metadata
        """
        file_type = file_type.lower()
        
        if file_type == 'pdf':
            return self.extract_text_from_pdf(file_path)
        elif file_type in ['jpg', 'jpeg', 'png', 'tiff', 'bmp']:
            return self.extract_text_from_image(file_path)
        else:
            return {
                'text': '',
                'confidence': 0,
                'success': False,
                'error': f'Unsupported file type: {file_type}'
            }
    
    def preprocess_image(self, image_path: str, output_path: str) -> bool:
        """
        Preprocess image for better OCR results
        Applies: grayscale conversion, contrast enhancement, noise reduction
        """
        try:
            from PIL import ImageEnhance, ImageFilter
            
            image = Image.open(image_path)
            
            # Convert to grayscale
            if image.mode != 'L':
                image = image.convert('L')
            
            # Enhance contrast
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)
            
            # Reduce noise
            image = image.filter(ImageFilter.MedianFilter(size=3))
            
            # Save preprocessed image
            image.save(output_path)
            
            return True
        
        except Exception as e:
            print(f"Preprocessing error: {e}")
            return False


# Singleton instance
_ocr_service = None


def get_ocr_service() -> OCRService:
    """Get or create OCR service instance"""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service