"""
PDF Processor
Utilities for handling PDF files
"""

import PyPDF2
import pdf2image
from PIL import Image
from typing import List, Dict, Optional
import tempfile
import os


class PDFProcessor:
    """Utility class for PDF processing"""
    
    @staticmethod
    def extract_text_from_pdf(pdf_path: str) -> Dict:
        """
        Extract text from PDF using PyPDF2
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with extracted text and metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                num_pages = len(pdf_reader.pages)
                text_by_page = []
                
                for page_num in range(num_pages):
                    page = pdf_reader.pages[page_num]
                    text = page.extract_text()
                    text_by_page.append({
                        'page_number': page_num + 1,
                        'text': text
                    })
                
                # Combine all text
                full_text = '\n\n'.join([p['text'] for p in text_by_page])
                
                return {
                    'success': True,
                    'text': full_text,
                    'pages': num_pages,
                    'text_by_page': text_by_page,
                    'metadata': {
                        'pages': num_pages,
                        'method': 'pypdf2'
                    }
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': '',
                'pages': 0
            }
    
    @staticmethod
    def convert_pdf_to_images(pdf_path: str, dpi: int = 300) -> List[str]:
        """
        Convert PDF pages to images
        
        Args:
            pdf_path: Path to PDF file
            dpi: Resolution for conversion
            
        Returns:
            List of paths to generated images
        """
        try:
            images = pdf2image.convert_from_path(pdf_path, dpi=dpi)
            
            image_paths = []
            temp_dir = tempfile.gettempdir()
            
            for i, image in enumerate(images):
                image_path = os.path.join(temp_dir, f"pdf_page_{i+1}.jpg")
                image.save(image_path, 'JPEG')
                image_paths.append(image_path)
            
            return image_paths
        
        except Exception as e:
            print(f"PDF to image conversion error: {e}")
            return []
    
    @staticmethod
    def get_pdf_metadata(pdf_path: str) -> Dict:
        """
        Extract metadata from PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Dictionary with PDF metadata
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                metadata = pdf_reader.metadata
                num_pages = len(pdf_reader.pages)
                
                return {
                    'success': True,
                    'pages': num_pages,
                    'title': metadata.get('/Title', ''),
                    'author': metadata.get('/Author', ''),
                    'subject': metadata.get('/Subject', ''),
                    'creator': metadata.get('/Creator', ''),
                    'producer': metadata.get('/Producer', ''),
                    'creation_date': metadata.get('/CreationDate', ''),
                }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    @staticmethod
    def split_pdf(pdf_path: str, output_dir: str) -> List[str]:
        """
        Split PDF into individual pages
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save split PDFs
            
        Returns:
            List of paths to split PDF files
        """
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                num_pages = len(pdf_reader.pages)
                
                output_paths = []
                
                for page_num in range(num_pages):
                    pdf_writer = PyPDF2.PdfWriter()
                    pdf_writer.add_page(pdf_reader.pages[page_num])
                    
                    output_path = os.path.join(
                        output_dir,
                        f"page_{page_num + 1}.pdf"
                    )
                    
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                    
                    output_paths.append(output_path)
                
                return output_paths
        
        except Exception as e:
            print(f"PDF split error: {e}")
            return []
    
    @staticmethod
    def merge_pdfs(pdf_paths: List[str], output_path: str) -> bool:
        """
        Merge multiple PDFs into one
        
        Args:
            pdf_paths: List of paths to PDF files
            output_path: Path to save merged PDF
            
        Returns:
            True if successful, False otherwise
        """
        try:
            pdf_writer = PyPDF2.PdfWriter()
            
            for pdf_path in pdf_paths:
                with open(pdf_path, 'rb') as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    for page in pdf_reader.pages:
                        pdf_writer.add_page(page)
            
            with open(output_path, 'wb') as output_file:
                pdf_writer.write(output_file)
            
            return True
        
        except Exception as e:
            print(f"PDF merge error: {e}")
            return False
    
    @staticmethod
    def is_pdf_encrypted(pdf_path: str) -> bool:
        """
        Check if PDF is encrypted
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            True if encrypted, False otherwise
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return pdf_reader.is_encrypted
        except Exception:
            return False
    
    @staticmethod
    def get_page_count(pdf_path: str) -> int:
        """
        Get number of pages in PDF
        
        Args:
            pdf_path: Path to PDF file
            
        Returns:
            Number of pages
        """
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                return len(pdf_reader.pages)
        except Exception:
            return 0