"""
Graph ontology schema definitions.
Defines node types, relationship types, and properties.
"""
from enum import Enum
from typing import List, Dict
from dataclasses import dataclass


class NodeType(str, Enum):
    """Graph node types."""
    COMPANY = "Company"
    PERSON = "Person"
    LOCATION = "Location"
    FINANCIAL_METRIC = "FinancialMetric"
    PRODUCT = "Product"
    RISK_FACTOR = "RiskFactor"
    TABLE_DATA = "TableData"
    CHART_DATA = "ChartData"


class RelationshipType(str, Enum):
    """Graph relationship types."""
    HAS_SUBSIDIARY = "HAS_SUBSIDIARY"
    HAS_EXECUTIVE = "HAS_EXECUTIVE"
    OPERATES_IN = "OPERATES_IN"
    REPORTS_METRIC = "REPORTS_METRIC"
    MANUFACTURES = "MANUFACTURES"
    COMPETES_WITH = "COMPETES_WITH"
    FACES_RISK = "FACES_RISK"
    DERIVED_FROM_TABLE = "DERIVED_FROM_TABLE"
    VISUALIZED_IN_CHART = "VISUALIZED_IN_CHART"
    MENTIONED_IN_SECTION = "MENTIONED_IN_SECTION"


@dataclass
class Entity:
    """Entity data structure."""
    name: str
    entity_type: NodeType
    properties: Dict
    confidence: float = 1.0
    source_chunk_id: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "name": self.name,
            "entity_type": self.entity_type.value,
            "properties": self.properties,
            "confidence": self.confidence,
            "source_chunk_id": self.source_chunk_id
        }


@dataclass
class Relationship:
    """Relationship data structure."""
    source_entity: str
    source_type: NodeType
    target_entity: str
    target_type: NodeType
    relationship_type: RelationshipType
    properties: Dict
    confidence: float = 1.0
    evidence: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "source_entity": self.source_entity,
            "source_type": self.source_type.value,
            "target_entity": self.target_entity,
            "target_type": self.target_type.value,
            "relationship_type": self.relationship_type.value,
            "properties": self.properties,
            "confidence": self.confidence,
            "evidence": self.evidence
        }


class GraphSchema:
    """
    Graph schema manager.
    Provides schema information and validation.
    """
    
    @staticmethod
    def get_node_properties(node_type: NodeType) -> List[str]:
        """Get required properties for a node type."""
        node_properties = {
            NodeType.COMPANY: ["ticker", "name", "cik", "sector", "industry"],
            NodeType.PERSON: ["name", "role"],
            NodeType.LOCATION: ["city", "state", "country"],
            NodeType.FINANCIAL_METRIC: ["name", "value", "unit", "period"],
            NodeType.PRODUCT: ["name", "category"],
            NodeType.RISK_FACTOR: ["category", "description"],
            NodeType.TABLE_DATA: ["table_id", "summary"],
            NodeType.CHART_DATA: ["chart_id", "chart_type", "description"]
        }
        return node_properties.get(node_type, [])
    
    @staticmethod
    def get_relationship_properties(rel_type: RelationshipType) -> List[str]:
        """Get required properties for a relationship type."""
        rel_properties = {
            RelationshipType.HAS_SUBSIDIARY: ["confidence_score"],
            RelationshipType.HAS_EXECUTIVE: ["confidence_score", "temporal_validity"],
            RelationshipType.OPERATES_IN: ["confidence_score"],
            RelationshipType.REPORTS_METRIC: ["confidence_score", "extraction_method"],
            RelationshipType.MANUFACTURES: ["confidence_score"],
            RelationshipType.COMPETES_WITH: ["confidence_score"],
            RelationshipType.FACES_RISK: ["confidence_score"],
            RelationshipType.DERIVED_FROM_TABLE: ["table_id"],
            RelationshipType.VISUALIZED_IN_CHART: ["chart_id"],
            RelationshipType.MENTIONED_IN_SECTION: ["section", "page_numbers"]
        }
        return rel_properties.get(rel_type, ["confidence_score"])
    
    @staticmethod
    def get_indexes() -> Dict[NodeType, List[str]]:
        """Get indexes for each node type."""
        return {
            NodeType.COMPANY: ["ticker", "cik", "name"],
            NodeType.PERSON: ["name"],
            NodeType.LOCATION: ["country"],
            NodeType.FINANCIAL_METRIC: ["name", "fiscal_year"],
            NodeType.PRODUCT: ["name"],
            NodeType.RISK_FACTOR: ["category"],
            NodeType.TABLE_DATA: ["table_id"],
            NodeType.CHART_DATA: ["chart_id"]
        }
