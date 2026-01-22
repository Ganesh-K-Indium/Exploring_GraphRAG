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
            
            # Look for section headers line by line
            lines = text.split('\n')
            for line in lines:
                line_stripped = line.strip()
                
                # Check for section markers
                for marker_pattern in self.section_markers:
                    pattern = re.compile(marker_pattern, re.MULTILINE)
                    match = pattern.search(line_stripped)
                    
                    if match:
                        # Save previous section
                        if current_section and section_text:
                            sections[current_section] = {
                                "text": "\n".join(section_text),
                                "page_start": section_start_page,
                                "page_end": page_num - 1,
                                "title": current_section,
                                "word_count": len("\n".join(section_text).split())
                            }
                        
                        # Extract section title
                        section_title = line_stripped[:100].strip()
                        current_section = section_title
                        section_text = []
                        section_start_page = page_num
                        break
            
            # Add text to current section
            if current_section:
                section_text.append(text)
        
        # Save last section
        if current_section and section_text:
            sections[current_section] = {
                "text": "\n".join(section_text),
                "page_start": section_start_page,
                "page_end": pages[-1]["page_num"],
                "title": current_section,
                "word_count": len("\n".join(section_text).split())
            }
        
        # If no sections found, create a default section
        if not sections and pages:
            all_text = "\n".join([p["text"] for p in pages])
            sections["full_document"] = {
                "text": all_text,
                "page_start": 1,
                "page_end": pages[-1]["page_num"],
                "title": "Full Document",
                "word_count": len(all_text.split())
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
        Uses character-based chunking with safety limits for token counts.
        
        Args:
            text: Text to chunk
            start_page: Starting page number
        
        Returns:
            List of chunk dictionaries
        """
        chunks = []
        
        # Use smaller chunk size to ensure we stay under 8192 token limit
        # 1 token ≈ 4 characters, so 1024 chars ≈ 256 tokens
        # This gives us safety margin for 8192 token limit
        safe_chunk_size = min(self.chunk_size, 3000)  # Max ~750 tokens
        
        # Split by paragraphs first
        paragraphs = text.split("\n\n")
        
        current_chunk = []
        current_length = 0
        
        for para in paragraphs:
            para_length = len(para)
            
            # If single paragraph is too long, split it
            if para_length > safe_chunk_size:
                # Split long paragraph into sentences
                sentences = para.split('. ')
                for sentence in sentences:
                    if current_length + len(sentence) > safe_chunk_size and current_chunk:
                        # Save current chunk
                        chunk_text = "\n\n".join(current_chunk)
                        chunks.append({
                            "text": chunk_text,
                            "length": len(chunk_text),
                            "pages": [start_page]
                        })
                        current_chunk = []
                        current_length = 0
                    
                    current_chunk.append(sentence)
                    current_length += len(sentence)
            elif current_length + para_length > safe_chunk_size and current_chunk:
                # Save current chunk
                chunk_text = "\n\n".join(current_chunk)
                chunks.append({
                    "text": chunk_text,
                    "length": len(chunk_text),
                    "pages": [start_page]
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
