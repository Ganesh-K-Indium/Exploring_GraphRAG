"""
Graph-based retrieval using Neo4j.
Performs graph traversal and pattern matching.
"""
from typing import List, Dict, Optional
from loguru import logger

from src.databases.neo4j_manager import Neo4jManager
from src.ontology.schema import NodeType, RelationshipType


class GraphRetriever:
    """
    Graph retrieval using Neo4j.
    Performs entity-based queries and graph traversal.
    """
    
    def __init__(self, neo4j_manager: Neo4jManager):
        """
        Initialize graph retriever.
        
        Args:
            neo4j_manager: Neo4j database manager
        """
        self.neo4j = neo4j_manager
        logger.info("GraphRetriever initialized")
    
    def find_entity_relationships(
        self,
        entity_name: str,
        relationship_types: Optional[List[RelationshipType]] = None,
        max_depth: int = 2
    ) -> Dict:
        """
        Find all relationships for an entity.
        
        Args:
            entity_name: Entity name
            relationship_types: Optional filter by relationship types
            max_depth: Maximum traversal depth
        
        Returns:
            Dictionary with entity and relationships
        """
        related = self.neo4j.get_related_entities(
            entity_name,
            relationship_types,
            max_depth
        )
        
        return {
            "entity": entity_name,
            "related_entities": related,
            "count": len(related)
        }
    
    def find_companies_by_sector(self, sector: str) -> List[Dict]:
        """
        Find all companies in a sector.
        
        Args:
            sector: Sector name
        
        Returns:
            List of companies
        """
        query = """
        MATCH (c:Company {sector: $sector})
        RETURN c, elementId(c) as node_id
        """
        
        results = self.neo4j.query_cypher(query, {"sector": sector})
        
        companies = []
        for record in results:
            company = dict(record["c"])
            company["node_id"] = record["node_id"]
            companies.append(company)
        
        return companies
    
    def find_executive_changes(
        self,
        company_name: str,
        time_period: Optional[str] = None
    ) -> List[Dict]:
        """
        Find executive changes for a company.
        
        Args:
            company_name: Company name
            time_period: Optional time period filter
        
        Returns:
            List of executive relationships
        """
        query = """
        MATCH (c:Company {name: $company})-[r:HAS_EXECUTIVE]->(p:Person)
        RETURN p, r, elementId(p) as node_id
        ORDER BY r.temporal_validity DESC
        """
        
        results = self.neo4j.query_cypher(query, {"company": company_name})
        
        executives = []
        for record in results:
            exec_data = dict(record["p"])
            exec_data["node_id"] = record["node_id"]
            exec_data["relationship"] = dict(record["r"])
            executives.append(exec_data)
        
        return executives
    
    def compare_companies(
        self,
        company_names: List[str],
        metric_name: Optional[str] = None
    ) -> Dict:
        """
        Compare multiple companies.
        
        Args:
            company_names: List of company names
            metric_name: Optional metric to compare
        
        Returns:
            Comparison data
        """
        comparison = {
            "companies": [],
            "common_metrics": [],
            "relationships": []
        }
        
        for company in company_names:
            # Get company node
            entity = self.neo4j.get_entity_by_name(company, NodeType.COMPANY)
            if entity:
                comparison["companies"].append(entity)
                
                # Get metrics
                if metric_name:
                    metrics_query = """
                    MATCH (c:Company {name: $company})-[:REPORTS_METRIC]->(m:FinancialMetric)
                    WHERE m.name CONTAINS $metric
                    RETURN m
                    ORDER BY m.fiscal_year DESC
                    """
                    
                    metrics = self.neo4j.query_cypher(
                        metrics_query,
                        {"company": company, "metric": metric_name}
                    )
                    
                    comparison["common_metrics"].extend(metrics)
        
        return comparison
    
    def find_supply_chain(
        self,
        company_name: str,
        direction: str = "both"
    ) -> Dict:
        """
        Find supply chain relationships.
        
        Args:
            company_name: Company name
            direction: "upstream", "downstream", or "both"
        
        Returns:
            Supply chain data
        """
        if direction == "upstream":
            rel_direction = "<-"
        elif direction == "downstream":
            rel_direction = "->"
        else:
            rel_direction = "-"
        
        query = f"""
        MATCH path = (c:Company {{name: $company}}){rel_direction}[:HAS_SUBSIDIARY|COMPETES_WITH*1..2]-(related:Company)
        RETURN related, relationships(path) as rels
        """
        
        results = self.neo4j.query_cypher(query, {"company": company_name})
        
        return {
            "company": company_name,
            "supply_chain": results
        }
