"""
LLM-based relationship extraction using GPT-4o.
Extracts complex relationships between entities with financial analyst expertise.
"""
from typing import List, Dict
import json
from loguru import logger
from openai import OpenAI

from src.config import settings
from .schema import Relationship, NodeType, RelationshipType
from .financial_analyst_prompt import FINANCIAL_ANALYST_EXTRACTION_PROMPT


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
        # Increased max_tokens for comprehensive financial extraction
        self.max_tokens = self.config.get("max_tokens", 8192)
        
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
            
            # Build comprehensive properties dict
            properties = {
                "confidence_score": rel_dict.get("confidence", 0.8),
                "source_chunk_id": chunk_id,
                "temporal": rel_dict.get("temporal", "")
            }
            
            # Add any additional properties from the LLM response
            additional_props = [
                "role", "value", "unit", "metric_name", "severity",
                "region", "acquisition_price", "currency", "fiscal_year",
                "quarter", "period", "percentage", "category"
            ]
            for prop in additional_props:
                if prop in rel_dict:
                    properties[prop] = rel_dict[prop]
            
            relationship = Relationship(
                source_entity=rel_dict.get("source_entity", ""),
                source_type=source_type,
                target_entity=rel_dict.get("target_entity", ""),
                target_type=target_type,
                relationship_type=rel_type,
                properties=properties,
                confidence=rel_dict.get("confidence", 0.8),
                evidence=rel_dict.get("evidence", "")
            )
            
            return relationship
        
        except Exception as e:
            logger.error(f"Failed to convert dict to relationship: {e}")
            return None
    
    def _map_relationship_type(self, rel_type_str: str) -> RelationshipType | None:
        """Map string to RelationshipType enum with comprehensive financial mappings."""
        rel_map = {
            # Structure
            "has_subsidiary": RelationshipType.HAS_SUBSIDIARY,
            "parent_of": RelationshipType.PARENT_OF,
            "controls": RelationshipType.CONTROLS,
            "owns": RelationshipType.OWNS,
            
            # Segments
            "operates_segment": RelationshipType.OPERATES_SEGMENT,
            "reports_segment": RelationshipType.REPORTS_SEGMENT,
            "segment_generates_revenue": RelationshipType.SEGMENT_GENERATES_REVENUE,
            "operates_in_market": RelationshipType.OPERATES_IN_MARKET,
            "operates_in_geography": RelationshipType.OPERATES_IN_GEOGRAPHY,
            
            # Management
            "has_executive": RelationshipType.HAS_EXECUTIVE,
            "serves_as": RelationshipType.SERVES_AS,
            "manages": RelationshipType.MANAGES,
            "has_board_member": RelationshipType.HAS_BOARD_MEMBER,
            "governs": RelationshipType.GOVERNS,
            "reports_to": RelationshipType.REPORTS_TO,
            "oversees": RelationshipType.OVERSEES,
            "audits": RelationshipType.AUDITS,
            
            # Products
            "sells_product": RelationshipType.SELLS_PRODUCT,
            "offers_service": RelationshipType.OFFERS_SERVICE,
            "manufactures": RelationshipType.MANUFACTURES,
            "produces": RelationshipType.PRODUCES,
            "distributes": RelationshipType.DISTRIBUTES,
            
            # Customers
            "has_customer": RelationshipType.HAS_CUSTOMER,
            "serves_customer": RelationshipType.SERVES_CUSTOMER,
            "generates_revenue_from": RelationshipType.GENERATES_REVENUE_FROM,
            "contract_with": RelationshipType.CONTRACT_WITH,
            
            # Financial
            "reports_metric": RelationshipType.REPORTS_METRIC,
            "contains_line_item": RelationshipType.CONTAINS_LINE_ITEM,
            "measures_performance": RelationshipType.MEASURES_PERFORMANCE,
            "has_revenue": RelationshipType.HAS_REVENUE,
            "has_earnings": RelationshipType.HAS_EARNINGS,
            "has_margin": RelationshipType.HAS_MARGIN,
            "projects_forecast": RelationshipType.PROJECTS_FORECAST,
            
            # Capital
            "issues_debt": RelationshipType.ISSUES_DEBT,
            "issues_equity": RelationshipType.ISSUES_EQUITY,
            "has_credit_facility": RelationshipType.HAS_CREDIT_FACILITY,
            "trades_on": RelationshipType.TRADES_ON,
            "has_ticker": RelationshipType.HAS_TICKER,
            "has_share_class": RelationshipType.HAS_SHARE_CLASS,
            
            # Assets
            "owns_asset": RelationshipType.OWNS_ASSET,
            "owes_liability": RelationshipType.OWES_LIABILITY,
            "has_goodwill": RelationshipType.HAS_GOODWILL,
            "has_intangible": RelationshipType.HAS_INTANGIBLE,
            
            # Risk
            "faces_risk": RelationshipType.FACES_RISK,
            "risk_threatens": RelationshipType.RISK_THREATENS,
            "subject_to_regulation": RelationshipType.SUBJECT_TO_REGULATION,
            "has_legal_case": RelationshipType.HAS_LEGAL_CASE,
            
            # Contracts
            "has_contract": RelationshipType.HAS_CONTRACT,
            "contract_generates_revenue": RelationshipType.CONTRACT_GENERATES_REVENUE,
            "has_lease": RelationshipType.HAS_LEASE,
            "has_license": RelationshipType.HAS_LICENSE,
            
            # Corporate Actions
            "acquired": RelationshipType.ACQUIRED,
            "acquisition_adds_revenue": RelationshipType.ACQUISITION_ADDS_REVENUE,
            "merged_with": RelationshipType.MERGED_WITH,
            "divested": RelationshipType.DIVESTED,
            "restructured": RelationshipType.RESTRUCTURED,
            "impaired": RelationshipType.IMPAIRED,
            
            # Geography
            "headquartered_at": RelationshipType.HEADQUARTERED_AT,
            "has_facility": RelationshipType.HAS_FACILITY,
            "located_in": RelationshipType.LOCATED_IN,
            "operates_in": RelationshipType.OPERATES_IN_MARKET,
            
            # Competition
            "competes_with": RelationshipType.COMPETES_WITH,
            
            # Regulatory
            "files_with": RelationshipType.FILES_WITH,
            "incorporated_in": RelationshipType.INCORPORATED_IN,
            "complies_with": RelationshipType.COMPLIES_WITH,
            
            # Temporal
            "has_fiscal_year": RelationshipType.HAS_FISCAL_YEAR,
            "valid_as_of": RelationshipType.VALID_AS_OF,
            "reported_in_period": RelationshipType.REPORTED_IN_PERIOD,
        }
        
        key = rel_type_str.lower().strip().replace(" ", "_")
        result = rel_map.get(key)
        
        if not result:
            logger.warning(f"Unknown relationship type: {rel_type_str}")
        
        return result
    
    def _map_entity_type(self, type_str: str) -> NodeType | None:
        """Map string to NodeType enum with comprehensive financial mappings."""
        type_map = {
            # Core Company
            "company": NodeType.COMPANY,
            "subsidiary": NodeType.SUBSIDIARY,
            "segment": NodeType.SEGMENT,
            "businessunit": NodeType.BUSINESS_UNIT,
            "business_unit": NodeType.BUSINESS_UNIT,
            "jointventure": NodeType.JOINT_VENTURE,
            "joint_venture": NodeType.JOINT_VENTURE,
            "legalentity": NodeType.LEGAL_ENTITY,
            "legal_entity": NodeType.LEGAL_ENTITY,
            
            # Management
            "person": NodeType.PERSON,
            "executive": NodeType.EXECUTIVE,
            "boardmember": NodeType.BOARD_MEMBER,
            "board_member": NodeType.BOARD_MEMBER,
            "committee": NodeType.COMMITTEE,
            "auditor": NodeType.AUDITOR,
            
            # Products & Markets
            "product": NodeType.PRODUCT,
            "service": NodeType.SERVICE,
            "productline": NodeType.PRODUCT_LINE,
            "product_line": NodeType.PRODUCT_LINE,
            "customer": NodeType.CUSTOMER,
            "customersegment": NodeType.CUSTOMER_SEGMENT,
            "customer_segment": NodeType.CUSTOMER_SEGMENT,
            "location": NodeType.LOCATION,
            "market": NodeType.MARKET,
            "geography": NodeType.GEOGRAPHY,
            
            # Financial
            "financialmetric": NodeType.FINANCIAL_METRIC,
            "financial_metric": NodeType.FINANCIAL_METRIC,
            "metric": NodeType.FINANCIAL_METRIC,
            "kpi": NodeType.KPI,
            "ratio": NodeType.RATIO,
            "lineitem": NodeType.LINE_ITEM,
            "line_item": NodeType.LINE_ITEM,
            "financialstatement": NodeType.FINANCIAL_STATEMENT,
            "financial_statement": NodeType.FINANCIAL_STATEMENT,
            "account": NodeType.ACCOUNT,
            
            # Capital
            "equity": NodeType.EQUITY,
            "debt": NodeType.DEBT,
            "creditfacility": NodeType.CREDIT_FACILITY,
            "credit_facility": NodeType.CREDIT_FACILITY,
            "stock": NodeType.STOCK,
            "shareclass": NodeType.SHARE_CLASS,
            "share_class": NodeType.SHARE_CLASS,
            
            # Assets
            "asset": NodeType.ASSET,
            "liability": NodeType.LIABILITY,
            "intangibleasset": NodeType.INTANGIBLE_ASSET,
            "intangible_asset": NodeType.INTANGIBLE_ASSET,
            "intangible": NodeType.INTANGIBLE_ASSET,
            "goodwill": NodeType.GOODWILL,
            "property": NodeType.PROPERTY,
            
            # Risk & Legal
            "riskfactor": NodeType.RISK_FACTOR,
            "risk_factor": NodeType.RISK_FACTOR,
            "risk": NodeType.RISK_FACTOR,
            "legalcase": NodeType.LEGAL_CASE,
            "legal_case": NodeType.LEGAL_CASE,
            "regulation": NodeType.REGULATION,
            "regulatorybody": NodeType.REGULATORY_BODY,
            "regulatory_body": NodeType.REGULATORY_BODY,
            "compliance": NodeType.COMPLIANCE,
            
            # Contracts
            "contract": NodeType.CONTRACT,
            "lease": NodeType.LEASE,
            "license": NodeType.LICENSE,
            "agreement": NodeType.AGREEMENT,
            
            # Corporate Actions
            "acquisition": NodeType.ACQUISITION,
            "merger": NodeType.MERGER,
            "divestiture": NodeType.DIVESTITURE,
            "restructuring": NodeType.RESTRUCTURING,
            
            # Temporal
            "date": NodeType.DATE,
            "fiscalperiod": NodeType.FISCAL_PERIOD,
            "fiscal_period": NodeType.FISCAL_PERIOD,
        }
        
        key = type_str.lower().strip().replace(" ", "")
        result = type_map.get(key)
        
        if not result:
            logger.warning(f"Unknown entity type: {type_str}, defaulting to COMPANY")
            # Default to COMPANY for unknown types rather than None
            return NodeType.COMPANY
        
        return result
    
    def _get_default_prompt(self) -> str:
        """Get comprehensive financial analyst extraction prompt."""
        return FINANCIAL_ANALYST_EXTRACTION_PROMPT
