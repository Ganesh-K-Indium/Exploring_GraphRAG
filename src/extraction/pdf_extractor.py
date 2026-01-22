"""
Main PDF extraction orchestrator.
Coordinates text, table, and image extraction from 10-K PDFs.
"""
from typing import Dict, List, Optional
from pathlib import Path
import hashlib
from loguru import logger
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

from .text_processor import TextProcessor
from .table_processor import TableProcessor
from .image_processor import ImageProcessor
from .vision_analyzer import VisionAnalyzer


class PDFExtractor:
    """
    Orchestrates multimodal extraction from PDF files.
    Extracts text, tables, images, and charts with proper context.
    """
    
    def __init__(
        self,
        config: Dict,
        output_dir: str = "data/extracted",
        use_vision: bool = True,
        max_workers: int = 4
    ):
        """
        Initialize PDF extractor.
        
        Args:
            config: Extraction configuration dictionary
            output_dir: Directory to save extracted content
            use_vision: Whether to use Vision API for chart analysis
            max_workers: Number of parallel workers
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        
        # Initialize processors
        self.text_processor = TextProcessor(config.get("text", {}))
        self.table_processor = TableProcessor(config.get("tables", {}))
        self.image_processor = ImageProcessor(config.get("images", {}))
        
        self.vision_analyzer = None
        if use_vision and config.get("images", {}).get("use_vision_api"):
            self.vision_analyzer = VisionAnalyzer()
        
        logger.info("PDFExtractor initialized")
    
    def extract_from_pdf(
        self,
        pdf_path: str,
        metadata: Optional[Dict] = None
    ) -> Dict:
        """
        Extract all content from a 10-K PDF.
        
        Args:
            pdf_path: Path to PDF file
            metadata: Optional metadata (ticker, filing_date, etc.)
        
        Returns:
            Dictionary containing all extracted content
        """
        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF not found: {pdf_path}")
        
        logger.info(f"Starting extraction from {pdf_path.name}")
        
        # Generate document ID
        doc_id = self._generate_doc_id(pdf_path)
        
        # Extract components in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit extraction tasks
            text_future = executor.submit(
                self.text_processor.extract_text,
                str(pdf_path)
            )
            table_future = executor.submit(
                self.table_processor.extract_tables,
                str(pdf_path)
            )
            image_future = executor.submit(
                self.image_processor.extract_images,
                str(pdf_path),
                str(self.output_dir / "images" / doc_id)
            )
            
            # Wait for results
            text_data = text_future.result()
            table_data = table_future.result()
            image_data = image_future.result()
        
        logger.info(
            f"Extracted {len(text_data['sections'])} sections, "
            f"{len(table_data)} tables, {len(image_data)} images"
        )
        
        # Analyze charts with Vision API if enabled
        if self.vision_analyzer:
            image_data = self._analyze_charts(image_data)
        
        # Create multimodal chunks
        chunks = self._create_multimodal_chunks(
            text_data,
            table_data,
            image_data,
            metadata or {}
        )
        
        result = {
            "document_id": doc_id,
            "file_name": pdf_path.name,
            "metadata": metadata or {},
            "sections": text_data.get("sections", {}),
            "text_data": text_data,
            "tables": table_data,
            "images": image_data,
            "chunks": chunks,
            "stats": {
                "num_sections": len(text_data.get("sections", {})),
                "num_tables": len(table_data),
                "num_images": len(image_data),
                "num_chunks": len(chunks)
            }
        }
        
        logger.info(f"Extraction complete: {result['stats']}")
        return result
    
    def _generate_doc_id(self, pdf_path: Path) -> str:
        """Generate unique document ID from file path."""
        return hashlib.md5(str(pdf_path).encode()).hexdigest()[:16]
    
    def _analyze_charts(self, image_data: List[Dict]) -> List[Dict]:
        """Analyze charts using Vision API."""
        logger.info(f"Analyzing {len(image_data)} images with Vision API")
        
        charts = [img for img in image_data if img.get("is_chart")]
        
        with ThreadPoolExecutor(max_workers=2) as executor:
            futures = {
                executor.submit(
                    self.vision_analyzer.analyze_chart,
                    chart["image_path"]
                ): chart
                for chart in charts
            }
            
            for future in tqdm(as_completed(futures), total=len(futures)):
                chart = futures[future]
                try:
                    analysis = future.result()
                    chart.update(analysis)
                except Exception as e:
                    logger.error(f"Failed to analyze chart: {e}")
        
        return image_data
    
    def _create_multimodal_chunks(
        self,
        text_data: Dict,
        table_data: List[Dict],
        image_data: List[Dict],
        metadata: Dict
    ) -> List[Dict]:
        """
        Create multimodal chunks that preserve context across modalities.
        
        Combines text, tables, and images that appear near each other
        in the document.
        """
        chunks = []
        chunk_config = self.config.get("chunking", {})
        context_window = chunk_config.get("context_window", 2)
        
        # Create text chunks
        for section_name, section_data in text_data["sections"].items():
            text_chunks = self.text_processor.chunk_text(
                section_data["text"],
                section_data["page_start"]
            )
            
            for chunk in text_chunks:
                chunk_dict = {
                    "chunk_id": self._generate_chunk_id(chunk),
                    "chunk_type": "text",
                    "text_content": chunk["text"],
                    "metadata": {
                        "section": section_name,
                        "page_numbers": chunk["pages"],
                        "modality": ["text"],
                        **metadata
                    },
                    "table_data": None,
                    "image_data": None
                }
                chunks.append(chunk_dict)
        
        # Create table chunks
        for table in table_data:
            chunk_dict = {
                "chunk_id": self._generate_chunk_id(table),
                "chunk_type": "table",
                "text_content": table.get("description", ""),
                "metadata": {
                    "section": table.get("section", "Unknown"),
                    "page_numbers": [table["page"]],
                    "modality": ["table"],
                    "has_table": True,
                    **metadata
                },
                "table_data": table["data"],
                "image_data": None
            }
            chunks.append(chunk_dict)
        
        # Create image/chart chunks
        for image in image_data:
            if image.get("is_chart"):
                chunk_dict = {
                    "chunk_id": self._generate_chunk_id(image),
                    "chunk_type": "image",
                    "text_content": image.get("description", ""),
                    "metadata": {
                        "section": image.get("section", "Unknown"),
                        "page_numbers": [image["page"]],
                        "modality": ["image"],
                        "has_chart": True,
                        "chart_type": image.get("chart_type", "unknown"),
                        **metadata
                    },
                    "table_data": None,
                    "image_data": {
                        "image_path": image["image_path"],
                        "description": image.get("description", ""),
                        "extracted_data": image.get("data_points", {}),
                        "insights": image.get("insights", [])
                    }
                }
                chunks.append(chunk_dict)
        
        # TODO: Implement mixed chunks (nearby text + table + image)
        # This would require proximity detection and context merging
        
        logger.info(f"Created {len(chunks)} multimodal chunks")
        return chunks
    
    def _generate_chunk_id(self, chunk: Dict) -> str:
        """Generate unique chunk ID."""
        content = str(chunk)
        return hashlib.md5(content.encode()).hexdigest()[:16]
