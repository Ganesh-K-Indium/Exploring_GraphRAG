"""
Vision API analyzer for charts and diagrams.
Uses GPT-4o Vision to extract data and insights from financial charts.
"""
from typing import Dict, Optional
import base64
from pathlib import Path
from loguru import logger
from openai import OpenAI

from src.config import settings


class VisionAnalyzer:
    """
    Analyzes charts and diagrams using GPT-4o Vision API.
    Extracts data points, identifies chart types, and generates descriptions.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize vision analyzer.
        
        Args:
            api_key: OpenAI API key (optional, uses settings if not provided)
        """
        self.client = OpenAI(
            api_key=api_key or settings.openai_api_key
        )
        self.model = "gpt-4o"
        
        self.analysis_prompt = """Analyze this financial chart/graph and extract:

1. Chart type (bar, line, pie, scatter, etc.)
2. All data points and values (be precise)
3. Axis labels and units
4. Key insights and trends
5. Time period covered (if shown)
6. What financial metrics or concepts are displayed

Provide a detailed textual description suitable for:
- Semantic search/embedding
- Understanding by someone who can't see the image
- Financial analysis

Format your response as JSON:
{
  "chart_type": "...",
  "title": "...",
  "data_points": {...},
  "axis_labels": {"x": "...", "y": "..."},
  "units": "...",
  "time_period": "...",
  "key_insights": ["...", "..."],
  "description": "A comprehensive textual description..."
}"""
        
        logger.info("VisionAnalyzer initialized")
    
    def analyze_chart(self, image_path: str) -> Dict:
        """
        Analyze a chart image using GPT-4o Vision.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with chart analysis
        """
        logger.info(f"Analyzing chart: {image_path}")
        
        try:
            # Read and encode image
            image_data = self._encode_image(image_path)
            
            # Get media type for data URL
            ext = Path(image_path).suffix.lower()
            media_type_map = {
                ".png": "image/png",
                ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg",
                ".webp": "image/webp",
                ".gif": "image/gif"
            }
            media_type = media_type_map.get(ext, "image/png")
            
            # Call GPT-4o Vision
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1024,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:{media_type};base64,{image_data}"
                                }
                            },
                            {
                                "type": "text",
                                "text": self.analysis_prompt
                            }
                        ]
                    }
                ]
            )
            
            # Parse response
            content = response.choices[0].message.content
            
            # Try to parse JSON response
            import json
            try:
                analysis = json.loads(content)
            except json.JSONDecodeError:
                # If not JSON, create structure from text
                analysis = {
                    "chart_type": "unknown",
                    "description": content,
                    "data_points": {},
                    "insights": []
                }
            
            logger.info(f"Chart analysis complete: {analysis.get('chart_type', 'unknown')}")
            return analysis
        
        except Exception as e:
            logger.error(f"Failed to analyze chart: {e}")
            return {
                "chart_type": "unknown",
                "description": "Failed to analyze chart",
                "data_points": {},
                "insights": [],
                "error": str(e)
            }
    
    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64."""
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
