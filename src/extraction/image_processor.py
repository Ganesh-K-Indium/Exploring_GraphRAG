"""
Image and chart extraction from PDFs using PyMuPDF.
Filters meaningful financial visuals and saves them.
"""
from typing import Dict, List
from pathlib import Path
import io
from PIL import Image
from loguru import logger
import fitz  # PyMuPDF


class ImageProcessor:
    """
    Extracts images and charts from PDF documents.
    Filters out decorative elements and focuses on financial visuals.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize image processor.
        
        Args:
            config: Image extraction configuration
        """
        self.config = config
        self.min_size_kb = config.get("min_size_kb", 50)
        self.max_size_kb = config.get("max_size_kb", 5000)
        self.extract_charts = config.get("extract_charts", True)
        
        logger.info("ImageProcessor initialized")
    
    def extract_images(
        self,
        pdf_path: str,
        output_dir: str
    ) -> List[Dict]:
        """
        Extract images from PDF.
        
        Args:
            pdf_path: Path to PDF file
            output_dir: Directory to save images
        
        Returns:
            List of image dictionaries with metadata
        """
        logger.info(f"Extracting images from {pdf_path}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        images = []
        
        try:
            doc = fitz.open(pdf_path)
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Get images from page
                image_list = page.get_images(full=True)
                
                for img_idx, img in enumerate(image_list):
                    try:
                        xref = img[0]
                        base_image = doc.extract_image(xref)
                        
                        if not base_image:
                            continue
                        
                        image_bytes = base_image["image"]
                        image_ext = base_image["ext"]
                        
                        # Check size
                        size_kb = len(image_bytes) / 1024
                        if size_kb < self.min_size_kb or size_kb > self.max_size_kb:
                            continue
                        
                        # Open image
                        image = Image.open(io.BytesIO(image_bytes))
                        
                        # Filter by dimensions
                        if not self._is_meaningful_image(image):
                            continue
                        
                        # Save image
                        image_filename = f"page{page_num+1}_img{img_idx}.{image_ext}"
                        image_path = output_path / image_filename
                        image.save(image_path)
                        
                        # Determine if it's likely a chart
                        is_chart = self._is_likely_chart(image)
                        
                        image_dict = {
                            "image_id": f"page{page_num+1}_img{img_idx}",
                            "page": page_num + 1,
                            "image_path": str(image_path),
                            "width": image.width,
                            "height": image.height,
                            "size_kb": size_kb,
                            "format": image_ext,
                            "is_chart": is_chart
                        }
                        
                        images.append(image_dict)
                    
                    except Exception as e:
                        logger.warning(f"Failed to extract image on page {page_num+1}: {e}")
            
            doc.close()
        
        except Exception as e:
            logger.error(f"Failed to extract images: {e}")
        
        logger.info(f"Extracted {len(images)} images ({sum(1 for i in images if i['is_chart'])} charts)")
        return images
    
    def _is_meaningful_image(self, image: Image.Image) -> bool:
        """
        Check if image is meaningful (not logo/decoration).
        
        Args:
            image: PIL Image
        
        Returns:
            True if image should be kept
        """
        width, height = image.size
        
        # Filter small images (likely logos)
        if width < 200 or height < 200:
            return False
        
        # Filter very wide or very tall images (likely headers/footers)
        aspect_ratio = width / height
        if aspect_ratio > 10 or aspect_ratio < 0.1:
            return False
        
        return True
    
    def _is_likely_chart(self, image: Image.Image) -> bool:
        """
        Heuristic to determine if image is likely a chart/graph.
        
        This is a simple heuristic. Vision API will provide better classification.
        
        Args:
            image: PIL Image
        
        Returns:
            True if likely a chart
        """
        width, height = image.size
        
        # Charts often have specific aspect ratios
        aspect_ratio = width / height
        if 0.5 <= aspect_ratio <= 2.0:
            # Reasonable chart dimensions
            if width >= 300 and height >= 200:
                return True
        
        return False
