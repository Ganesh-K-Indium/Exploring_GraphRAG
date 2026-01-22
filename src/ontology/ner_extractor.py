"""
NER-based entity extraction using spaCy.
Fast, rule-based extraction of entities from text.
"""
from typing import List, Dict, Tuple
import re
from loguru import logger
import spacy
from spacy.matcher import Matcher
from spacy.tokens import Span

from .schema import Entity, NodeType


class NERExtractor:
    """
    NER-based entity extraction.
    Uses spaCy with custom patterns for financial entities.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize NER extractor.
        
        Args:
            config: NER configuration
        """
        self.config = config
        model_name = config.get("model", "en_core_web_sm")
        
        try:
            self.nlp = spacy.load(model_name)
        except OSError:
            logger.warning(f"Model {model_name} not found. Downloading...")
            import subprocess
            subprocess.run(["python", "-m", "spacy", "download", model_name])
            self.nlp = spacy.load(model_name)
        
        # Add custom patterns
        self.matcher = Matcher(self.nlp.vocab)
        self._add_custom_patterns(config.get("custom_patterns", {}))
        
        logger.info("NERExtractor initialized")
    
    def extract_entities(self, text: str, chunk_id: str = "") -> List[Entity]:
        """
        Extract entities from text.
        
        Args:
            text: Input text
            chunk_id: Source chunk ID
        
        Returns:
            List of extracted entities
        """
        doc = self.nlp(text)
        entities = []
        
        # Extract standard NER entities
        for ent in doc.ents:
            entity_type = self._map_spacy_label(ent.label_)
            if entity_type:
                entity = Entity(
                    name=ent.text,
                    entity_type=entity_type,
                    properties={"text": ent.text, "label": ent.label_},
                    confidence=0.9,  # SpaCy confidence
                    source_chunk_id=chunk_id
                )
                entities.append(entity)
        
        # Extract custom pattern matches
        matches = self.matcher(doc)
        for match_id, start, end in matches:
            span = doc[start:end]
            pattern_name = self.nlp.vocab.strings[match_id]
            
            entity = Entity(
                name=span.text,
                entity_type=self._get_pattern_entity_type(pattern_name),
                properties={"text": span.text, "pattern": pattern_name},
                confidence=0.85,
                source_chunk_id=chunk_id
            )
            entities.append(entity)
        
        # Extract financial metrics from tables
        entities.extend(self._extract_financial_metrics(text, chunk_id))
        
        # Deduplicate entities
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _add_custom_patterns(self, patterns: Dict):
        """Add custom patterns to matcher."""
        # Financial metrics patterns
        financial_metrics = patterns.get("financial_metrics", [])
        for metric in financial_metrics:
            pattern = [{"LOWER": metric.lower()}]
            self.matcher.add(f"FINANCIAL_METRIC_{metric}", [pattern])
        
        # Currency patterns
        currency_patterns = patterns.get("currency", [])
        for pattern_dict in currency_patterns:
            if isinstance(pattern_dict, dict):
                pattern_text = pattern_dict.get("pattern", "")
                # Convert regex pattern to spaCy pattern
                # This is simplified - production would need better pattern conversion
                self.matcher.add("MONEY", [[{"TEXT": {"REGEX": pattern_text}}]])
        
        # Fiscal period patterns
        fiscal_patterns = patterns.get("fiscal_periods", [])
        for pattern_dict in fiscal_patterns:
            if isinstance(pattern_dict, dict):
                pattern_text = pattern_dict.get("pattern", "")
                self.matcher.add("FISCAL_PERIOD", [[{"TEXT": {"REGEX": pattern_text}}]])
    
    def _map_spacy_label(self, label: str) -> NodeType | None:
        """Map spaCy entity labels to our node types."""
        label_map = {
            "ORG": NodeType.COMPANY,
            "PERSON": NodeType.PERSON,
            "GPE": NodeType.LOCATION,
            "LOC": NodeType.LOCATION,
            "MONEY": NodeType.FINANCIAL_METRIC,
            "PRODUCT": NodeType.PRODUCT
        }
        return label_map.get(label)
    
    def _get_pattern_entity_type(self, pattern_name: str) -> NodeType:
        """Get entity type from pattern name."""
        if "FINANCIAL_METRIC" in pattern_name:
            return NodeType.FINANCIAL_METRIC
        elif "FISCAL_PERIOD" in pattern_name:
            return NodeType.FINANCIAL_METRIC
        else:
            return NodeType.COMPANY
    
    def _extract_financial_metrics(self, text: str, chunk_id: str) -> List[Entity]:
        """Extract financial metrics using regex patterns."""
        entities = []
        
        # Pattern for financial values
        # Examples: "$1.2 billion", "$500 million", "revenue of $X"
        value_pattern = r'\$[\d,]+(?:\.\d{1,2})?\s*(?:million|billion|thousand)?'
        
        matches = re.finditer(value_pattern, text, re.IGNORECASE)
        for match in matches:
            entity = Entity(
                name=match.group(),
                entity_type=NodeType.FINANCIAL_METRIC,
                properties={
                    "value": match.group(),
                    "extraction_method": "regex"
                },
                confidence=0.8,
                source_chunk_id=chunk_id
            )
            entities.append(entity)
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Entity]) -> List[Entity]:
        """Remove duplicate entities."""
        seen = set()
        unique_entities = []
        
        for entity in entities:
            key = (entity.name.lower(), entity.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(entity)
        
        return unique_entities
    
    def extract_from_table(self, table_data: Dict) -> List[Entity]:
        """
        Extract entities from structured table data.
        
        Args:
            table_data: Table dictionary
        
        Returns:
            List of entities
        """
        entities = []
        
        # Extract from column names
        columns = table_data.get("columns", [])
        for col in columns:
            # Check if column name contains financial metrics
            if any(metric in col.lower() for metric in ["revenue", "income", "ebitda", "eps"]):
                entity = Entity(
                    name=col,
                    entity_type=NodeType.FINANCIAL_METRIC,
                    properties={"source": "table_column"},
                    confidence=0.9,
                    source_chunk_id=table_data.get("table_id", "")
                )
                entities.append(entity)
        
        # Extract from table data
        data = table_data.get("data", [])
        for row in data:
            for key, value in row.items():
                # Extract monetary values
                if isinstance(value, str) and "$" in value:
                    entity = Entity(
                        name=value,
                        entity_type=NodeType.FINANCIAL_METRIC,
                        properties={
                            "value": value,
                            "column": key,
                            "source": "table_data"
                        },
                        confidence=0.95,
                        source_chunk_id=table_data.get("table_id", "")
                    )
                    entities.append(entity)
        
        return entities
