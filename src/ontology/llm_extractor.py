"""
LLM-based relationship extraction using GPT-4o.
Extracts complex relationships between entities.
"""
from typing import List, Dict
import json
from loguru import logger
from openai import OpenAI

from src.config import settings
from .schema import Relationship, NodeType, RelationshipType


class LLMExtractor:
    """
    LLM-based relationship extraction.
    Uses GPT-4o to extract complex entity relationships.
    """
    
    def __init__(self, api_key: str = None, config: Dict = None):
        """
        Initialize LLM extractor.
        
        Args:
            api_key: OpenAI API key
            config: LLM configuration
        """
        self.client = OpenAI(
            api_key=api_key or settings.openai_api_key
        )
        self.config = config or {}
        self.model = self.config.get("model", settings.llm_model)
        self.max_tokens = self.config.get("max_tokens", 4096)
        
        self.extraction_prompt = self.config.get(
            "relationship_extraction_prompt",
            self._get_default_prompt()
        )
        
        logger.info("LLMExtractor initialized")
    
    def extract_relationships(
        self,
        text: str,
        entities: List[Dict],
        chunk_id: str = ""
    ) -> List[Relationship]:
        """
        Extract relationships from text given known entities.
        
        Args:
            text: Input text
            entities: List of entities found in text
            chunk_id: Source chunk ID
        
        Returns:
            List of extracted relationships
        """
        if not text or not entities:
            return []
        
        # Prepare entity context
        entity_context = self._format_entities(entities)
        
        # Create prompt
        prompt = f"""{self.extraction_prompt}

TEXT:
{text}

KNOWN ENTITIES:
{entity_context}

Extract relationships between these entities."""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=0.0,
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            content = response.choices[0].message.content
            
            # Parse JSON response
            relationships_data = self._parse_response(content)
            
            # Convert to Relationship objects
            relationships = []
            for rel_dict in relationships_data:
                try:
                    rel = self._dict_to_relationship(rel_dict, chunk_id)
                    if rel:
                        relationships.append(rel)
                except Exception as e:
                    logger.warning(f"Failed to parse relationship: {e}")
            
            logger.info(f"Extracted {len(relationships)} relationships")
            return relationships
        
        except Exception as e:
            logger.error(f"Failed to extract relationships: {e}")
            return []
    
    def extract_from_table(
        self,
        table_data: Dict,
        table_description: str,
        entities: List[Dict]
    ) -> List[Relationship]:
        """
        Extract relationships from table data.
        
        Args:
            table_data: Structured table data
            table_description: Text description of table
            entities: Known entities
        
        Returns:
            List of relationships
        """
        # Simplified table data for prompt
        simplified_table = {
            "columns": table_data.get("columns", []),
            "sample_rows": table_data.get("data", [])[:3]
        }
        
        table_text = f"Table Description: {table_description}\n\nTable Data:\n{json.dumps(simplified_table, indent=2)}"
        
        return self.extract_relationships(
            table_text,
            entities,
            table_data.get("table_id", "")
        )
    
    def _format_entities(self, entities: List[Dict]) -> str:
        """Format entities for prompt."""
        entity_strs = []
        for ent in entities:
            if isinstance(ent, dict):
                name = ent.get("name", "")
                ent_type = ent.get("entity_type", "")
            else:
                name = getattr(ent, "name", "")
                ent_type = getattr(ent, "entity_type", "")
            
            entity_strs.append(f"- {name} ({ent_type})")
        
        return "\n".join(entity_strs)
    
    def _parse_response(self, content: str) -> List[Dict]:
        """Parse LLM response to extract relationships."""
        try:
            # Try to parse as JSON
            data = json.loads(content)
            return data.get("relationships", [])
        except json.JSONDecodeError:
            # Try to find JSON in text
            import re
            json_match = re.search(r'\{.*\}', content, re.DOTALL)
            if json_match:
                try:
                    data = json.loads(json_match.group())
                    return data.get("relationships", [])
                except json.JSONDecodeError:
                    pass
        
        logger.warning("Could not parse LLM response as JSON")
        return []
    
    def _dict_to_relationship(
        self,
        rel_dict: Dict,
        chunk_id: str
    ) -> Relationship | None:
        """Convert dictionary to Relationship object."""
        try:
            # Map relationship type string to enum
            rel_type_str = rel_dict.get("relationship_type", "")
            rel_type = self._map_relationship_type(rel_type_str)
            
            if not rel_type:
                return None
            
            # Map entity types
            source_type = self._map_entity_type(rel_dict.get("source_type", ""))
            target_type = self._map_entity_type(rel_dict.get("target_type", ""))
            
            if not source_type or not target_type:
                return None
            
            relationship = Relationship(
                source_entity=rel_dict.get("source_entity", ""),
                source_type=source_type,
                target_entity=rel_dict.get("target_entity", ""),
                target_type=target_type,
                relationship_type=rel_type,
                properties={
                    "confidence_score": rel_dict.get("confidence", 0.8),
                    "source_chunk_id": chunk_id,
                    "temporal": rel_dict.get("temporal", "")
                },
                confidence=rel_dict.get("confidence", 0.8),
                evidence=rel_dict.get("evidence", "")
            )
            
            return relationship
        
        except Exception as e:
            logger.error(f"Failed to convert dict to relationship: {e}")
            return None
    
    def _map_relationship_type(self, rel_type_str: str) -> RelationshipType | None:
        """Map string to RelationshipType enum."""
        rel_map = {
            "subsidiary": RelationshipType.HAS_SUBSIDIARY,
            "has_subsidiary": RelationshipType.HAS_SUBSIDIARY,
            "executive": RelationshipType.HAS_EXECUTIVE,
            "has_executive": RelationshipType.HAS_EXECUTIVE,
            "operates_in": RelationshipType.OPERATES_IN,
            "reports_metric": RelationshipType.REPORTS_METRIC,
            "reports": RelationshipType.REPORTS_METRIC,
            "manufactures": RelationshipType.MANUFACTURES,
            "competes_with": RelationshipType.COMPETES_WITH,
            "faces_risk": RelationshipType.FACES_RISK,
            "risk": RelationshipType.FACES_RISK
        }
        
        key = rel_type_str.lower().strip()
        return rel_map.get(key)
    
    def _map_entity_type(self, type_str: str) -> NodeType | None:
        """Map string to NodeType enum."""
        type_map = {
            "company": NodeType.COMPANY,
            "person": NodeType.PERSON,
            "location": NodeType.LOCATION,
            "metric": NodeType.FINANCIAL_METRIC,
            "financial_metric": NodeType.FINANCIAL_METRIC,
            "product": NodeType.PRODUCT,
            "risk": NodeType.RISK_FACTOR,
            "risk_factor": NodeType.RISK_FACTOR
        }
        
        key = type_str.lower().strip()
        return type_map.get(key)
    
    def _get_default_prompt(self) -> str:
        """Get default extraction prompt."""
        return """Extract structured relationships between entities from the following financial text.
Focus on:
- Corporate structure (subsidiaries, joint ventures, partnerships)
- Business relationships (customers, suppliers, distributors)
- Financial relationships (investments, debt, equity)
- Competitive relationships
- Executive changes and organizational structure
- Risk dependencies

Return JSON format:
{
  "relationships": [
    {
      "source_entity": "entity name",
      "source_type": "COMPANY|PERSON|LOCATION|PRODUCT|METRIC",
      "target_entity": "entity name",
      "target_type": "COMPANY|PERSON|LOCATION|PRODUCT|METRIC",
      "relationship_type": "relationship type",
      "confidence": 0.0-1.0,
      "evidence": "supporting text snippet",
      "temporal": "time period if mentioned"
    }
  ]
}"""
