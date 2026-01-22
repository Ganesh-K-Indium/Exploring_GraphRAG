"""
Graph ontology schema definitions.
Defines node types, relationship types, and properties.
"""
from enum import Enum
from typing import List, Dict
from dataclasses import dataclass


class NodeType(str, Enum):
    """Comprehensive node types for financial document analysis (10-K)."""
    # Core Company Structure
    COMPANY = "Company"
    SUBSIDIARY = "Subsidiary"
    SEGMENT = "Segment"
    BUSINESS_UNIT = "BusinessUnit"
    JOINT_VENTURE = "JointVenture"
    LEGAL_ENTITY = "LegalEntity"
    
    # Management & Governance
    PERSON = "Person"
    EXECUTIVE = "Executive"
    BOARD_MEMBER = "BoardMember"
    COMMITTEE = "Committee"
    AUDITOR = "Auditor"
    
    # Products & Services
    PRODUCT = "Product"
    SERVICE = "Service"
    PRODUCT_LINE = "ProductLine"
    
    # Customers & Markets
    CUSTOMER = "Customer"
    CUSTOMER_SEGMENT = "CustomerSegment"
    LOCATION = "Location"
    MARKET = "Market"
    GEOGRAPHY = "Geography"
    
    # Financial Statements & Metrics
    FINANCIAL_STATEMENT = "FinancialStatement"
    LINE_ITEM = "LineItem"
    ACCOUNT = "Account"
    FINANCIAL_METRIC = "FinancialMetric"
    KPI = "KPI"
    RATIO = "Ratio"
    
    # Capital Structure
    EQUITY = "Equity"
    DEBT = "Debt"
    CREDIT_FACILITY = "CreditFacility"
    STOCK = "Stock"
    SHARE_CLASS = "ShareClass"
    
    # Assets & Liabilities
    ASSET = "Asset"
    LIABILITY = "Liability"
    INTANGIBLE_ASSET = "IntangibleAsset"
    GOODWILL = "Goodwill"
    PROPERTY = "Property"
    
    # Risk & Legal
    RISK_FACTOR = "RiskFactor"
    LEGAL_CASE = "LegalCase"
    REGULATION = "Regulation"
    REGULATORY_BODY = "RegulatoryBody"
    COMPLIANCE = "Compliance"
    
    # Contracts & Agreements
    CONTRACT = "Contract"
    LEASE = "Lease"
    LICENSE = "License"
    AGREEMENT = "Agreement"
    
    # Corporate Actions
    ACQUISITION = "Acquisition"
    MERGER = "Merger"
    DIVESTITURE = "Divestiture"
    RESTRUCTURING = "Restructuring"
    
    # Temporal & Data
    DATE = "Date"
    FISCAL_PERIOD = "FiscalPeriod"
    TABLE_DATA = "TableData"
    CHART_DATA = "ChartData"


class RelationshipType(str, Enum):
    """Comprehensive relationship types for 10-K analysis."""
    # Corporate Structure
    HAS_SUBSIDIARY = "HAS_SUBSIDIARY"
    PARENT_OF = "PARENT_OF"
    CONTROLS = "CONTROLS"
    OWNS = "OWNS"
    
    # Segments & Operations
    OPERATES_SEGMENT = "OPERATES_SEGMENT"
    REPORTS_SEGMENT = "REPORTS_SEGMENT"
    SEGMENT_GENERATES_REVENUE = "SEGMENT_GENERATES_REVENUE"
    OPERATES_IN_MARKET = "OPERATES_IN_MARKET"
    OPERATES_IN_GEOGRAPHY = "OPERATES_IN_GEOGRAPHY"
    
    # Management & Governance
    HAS_EXECUTIVE = "HAS_EXECUTIVE"
    SERVES_AS = "SERVES_AS"
    MANAGES = "MANAGES"
    HAS_BOARD_MEMBER = "HAS_BOARD_MEMBER"
    GOVERNS = "GOVERNS"
    REPORTS_TO = "REPORTS_TO"
    OVERSEES = "OVERSEES"
    AUDITS = "AUDITS"
    
    # Products & Services
    SELLS_PRODUCT = "SELLS_PRODUCT"
    OFFERS_SERVICE = "OFFERS_SERVICE"
    MANUFACTURES = "MANUFACTURES"
    PRODUCES = "PRODUCES"
    DISTRIBUTES = "DISTRIBUTES"
    
    # Customers & Revenue
    HAS_CUSTOMER = "HAS_CUSTOMER"
    SERVES_CUSTOMER = "SERVES_CUSTOMER"
    GENERATES_REVENUE_FROM = "GENERATES_REVENUE_FROM"
    CONTRACT_WITH = "CONTRACT_WITH"
    
    # Financial Statements & Metrics
    REPORTS_METRIC = "REPORTS_METRIC"
    CONTAINS_LINE_ITEM = "CONTAINS_LINE_ITEM"
    MEASURES_PERFORMANCE = "MEASURES_PERFORMANCE"
    HAS_REVENUE = "HAS_REVENUE"
    HAS_EARNINGS = "HAS_EARNINGS"
    HAS_MARGIN = "HAS_MARGIN"
    PROJECTS_FORECAST = "PROJECTS_FORECAST"
    
    # Capital Structure
    ISSUES_DEBT = "ISSUES_DEBT"
    ISSUES_EQUITY = "ISSUES_EQUITY"
    HAS_CREDIT_FACILITY = "HAS_CREDIT_FACILITY"
    TRADES_ON = "TRADES_ON"
    HAS_TICKER = "HAS_TICKER"
    HAS_SHARE_CLASS = "HAS_SHARE_CLASS"
    DEBT_HAS_INTEREST_RATE = "DEBT_HAS_INTEREST_RATE"
    FACILITY_IMPOSES_COVENANTS = "FACILITY_IMPOSES_COVENANTS"
    
    # Assets & Liabilities
    OWNS_ASSET = "OWNS_ASSET"
    OWES_LIABILITY = "OWES_LIABILITY"
    ASSET_DEPRECIATES = "ASSET_DEPRECIATES"
    HAS_GOODWILL = "HAS_GOODWILL"
    HAS_INTANGIBLE = "HAS_INTANGIBLE"
    
    # Risk & Legal
    FACES_RISK = "FACES_RISK"
    RISK_THREATENS = "RISK_THREATENS"
    SUBJECT_TO_REGULATION = "SUBJECT_TO_REGULATION"
    HAS_LEGAL_CASE = "HAS_LEGAL_CASE"
    CREATES_LIABILITY = "CREATES_LIABILITY"
    CONSTRAINS_OPERATIONS = "CONSTRAINS_OPERATIONS"
    
    # Contracts & Obligations
    HAS_CONTRACT = "HAS_CONTRACT"
    CONTRACT_GENERATES_REVENUE = "CONTRACT_GENERATES_REVENUE"
    HAS_LEASE = "HAS_LEASE"
    LEASE_REQUIRES_PAYMENT = "LEASE_REQUIRES_PAYMENT"
    HAS_LICENSE = "HAS_LICENSE"
    LICENSE_PERMITS_USE = "LICENSE_PERMITS_USE"
    
    # Corporate Actions
    ACQUIRED = "ACQUIRED"
    ACQUISITION_ADDS_REVENUE = "ACQUISITION_ADDS_REVENUE"
    MERGED_WITH = "MERGED_WITH"
    DIVESTED = "DIVESTED"
    RESTRUCTURED = "RESTRUCTURED"
    IMPAIRED = "IMPAIRED"
    
    # Geographic & Facilities
    HEADQUARTERED_AT = "HEADQUARTERED_AT"
    HAS_FACILITY = "HAS_FACILITY"
    LOCATED_IN = "LOCATED_IN"
    
    # Competition
    COMPETES_WITH = "COMPETES_WITH"
    
    # Regulatory & Compliance
    FILES_WITH = "FILES_WITH"
    INCORPORATED_IN = "INCORPORATED_IN"
    COMPLIES_WITH = "COMPLIES_WITH"
    
    # Temporal
    HAS_FISCAL_YEAR = "HAS_FISCAL_YEAR"
    VALID_AS_OF = "VALID_AS_OF"
    REPORTED_IN_PERIOD = "REPORTED_IN_PERIOD"
    
    # Data Sources
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
            NodeType.CHART_DATA: ["chart_id", "chart_type", "description"],
            NodeType.BUSINESS_SEGMENT: ["name", "description"],
            NodeType.STOCK: ["ticker", "exchange", "class"],
            NodeType.REGULATORY_BODY: ["name", "jurisdiction"],
            NodeType.DATE: ["year", "quarter", "period"],
            NodeType.LEGAL_ENTITY: ["name", "jurisdiction", "type"]
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
