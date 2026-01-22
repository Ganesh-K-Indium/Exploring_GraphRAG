"""
Text extraction and chunking from PDFs.
Uses pypdf as primary method with fallbacks.
"""
from typing import Dict, List, Tuple
import re
from pathlib import Path
from loguru import logger

try:
    from pypdf import PdfReader
except ImportError:
    from PyPDF2 import PdfReader

import pdfplumber


class TextProcessor:
    """
    Extracts and processes text from PDF documents.
    Handles section detection and intelligent chunking.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize text processor.
        
        Args:
            config: Text extraction configuration
        """
        self.config = config
        self.chunk_size = config.get("chunk_size", 1024)
        self.chunk_overlap = config.get("chunk_overlap", 128)
        self.section_markers = config.get("section_markers", [])
        
        logger.info("TextProcessor initialized")
    
    def extract_text(self, pdf_path: str) -> Dict:
        """
        Extract text from PDF with section detection.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            Dictionary with sections and full text
        """
        logger.info(f"Extracting text from {pdf_path}")
        
        try:
            # Try pdfplumber first (better quality)
            with pdfplumber.open(pdf_path) as pdf:
                pages = []
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        pages.append({
                            "page_num": page.page_number,
                            "text": text
                        })
            
            if not pages:
                # Fallback to pypdf
                reader = PdfReader(pdf_path)
                pages = []
                for i, page in enumerate(reader.pages):
                    text = page.extract_text()
                    if text:
                        pages.append({
                            "page_num": i + 1,
                            "text": text
                        })
        
        except Exception as e:
            logger.error(f"Failed to extract text: {e}")
            return {"full_text": "", "sections": {}, "pages": []}
        
        # Combine all text
        full_text = "\n\n".join(p["text"] for p in pages)
        
        # Detect sections
        sections = self._detect_sections(pages)
        
        return {
            "full_text": full_text,
            "sections": sections,
            "pages": pages,
            "num_pages": len(pages)
        }
    
    def _detect_sections(self, pages: List[Dict]) -> Dict[str, Dict]:
        """
        Detect 10-K sections based on markers.
        
        Args:
            pages: List of page dictionaries
        
        Returns:
            Dictionary of sections with text and metadata
        """
        sections = {}
        current_section = None
        section_text = []
        section_start_page = None
        
        for page in pages:
            text = page["text"]
            page_num = page["page_num"]
            
            # Check for section markers
            for marker in self.section_markers:
                pattern = re.compile(marker, re.IGNORECASE)
                if pattern.search(text):
                    # Save previous section
                    if current_section and section_text:
                        sections[current_section] = {
                            "text": "\n".join(section_text),
                            "page_start": section_start_page,
                            "page_end": page_num - 1
                        }
                    
                    # Start new section
                    current_section = marker.replace(".", "").replace(" ", "_")
                    section_text = [text]
                    section_start_page = page_num
                    break
            else:
                # Continue current section
                if current_section:
                    section_text.append(text)
        
        # Save last section
        if current_section and section_text:
            sections[current_section] = {
                "text": "\n".join(section_text),
                "page_start": section_start_page,
                "page_end": pages[-1]["page_num"]
            }
        
        logger.info(f"Detected {len(sections)} sections")
        return sections
    
    def chunk_text(
        self,
        text: str,
        start_page: int = 1
    ) -> List[Dict]:
        """
        Chunk text with overlap for better context preservation.
        
        Args:
            text: Text to chunk
            start_page: Starting page number
        
        Returns:
            List of chunk dictionaries
        """
        # Simple character-based chunking
        # In production, use token-based chunking with tiktoken
        chunks = []
        
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            if current_length + para_length > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = "\n\n".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "length": len(chunk_text),
                    "pages": [start_page]  # Simplified page tracking
                })
                
                # Start new chunk with overlap
                overlap_text = current_chunk[-1] if current_chunk else ""
                current_chunk = [overlap_text, para] if overlap_text else [para]
                current_length = len(overlap_text) + para_length
            else:
                current_chunk.append(para)
                current_length += para_length
        
        # Add final chunk
        if current_chunk:
            chunk_text = "\n\n".join(current_chunk)
            chunks.append({
                "text": chunk_text,
                "length": len(chunk_text),
                "pages": [start_page]
            })
        
        return chunks
