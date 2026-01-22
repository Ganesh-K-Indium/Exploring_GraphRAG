"""
Neo4j graph database manager.
Handles entity and relationship storage and querying.
"""
from typing import List, Dict, Optional
from loguru import logger
from neo4j import GraphDatabase, Driver

from src.config import settings
from src.ontology.schema import Entity, Relationship, NodeType, RelationshipType


class Neo4jManager:
    """
    Manages Neo4j graph database operations.
    Handles entities, relationships, and graph queries.
    """
    
    def __init__(self, uri: str = None, user: str = None, password: str = None):
        """
        Initialize Neo4j manager.
        
        Args:
            uri: Neo4j URI
            user: Neo4j username
            password: Neo4j password
        """
        self.uri = uri or settings.neo4j_uri
        self.user = user or settings.neo4j_user
        self.password = password or settings.neo4j_password
        
        self.driver: Optional[Driver] = None
        self._connect()
        
        logger.info("Neo4jManager initialized")
    
    def _connect(self):
        """Connect to Neo4j database."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def create_indexes(self, schema_config: Dict = None):
        """
        Create indexes for efficient queries.
        
        Args:
            schema_config: Schema configuration with index definitions
        """
        with self.driver.session() as session:
            # Company indexes
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR (c:Company) ON (c.ticker)"
            )
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR (c:Company) ON (c.cik)"
            )
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR (c:Company) ON (c.name)"
            )
            
            # Person indexes
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR (p:Person) ON (p.name)"
            )
            
            # FinancialMetric indexes
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR (m:FinancialMetric) ON (m.name)"
            )
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR (m:FinancialMetric) ON (m.fiscal_year)"
            )
            
            # Location indexes
            session.run(
                "CREATE INDEX IF NOT EXISTS FOR (l:Location) ON (l.country)"
            )
        
        logger.info("Neo4j indexes created")
    
    def create_entity(self, entity: Entity, qdrant_point_id: str = None) -> str:
        """
        Create or update entity node.
        
        Args:
            entity: Entity object
            qdrant_point_id: Associated Qdrant point ID
        
        Returns:
            Neo4j node ID
        """
        with self.driver.session() as session:
            properties = entity.properties.copy()
            properties["name"] = entity.name
            properties["confidence"] = entity.confidence
            
            if qdrant_point_id:
                properties["qdrant_point_ids"] = [qdrant_point_id]
            
            # Create or merge node
            query = f"""
            MERGE (n:{entity.entity_type.value} {{name: $name}})
            SET n += $properties
            RETURN elementId(n) as node_id
            """
            
            result = session.run(query, name=entity.name, properties=properties)
            record = result.single()
            
            if record:
                return record["node_id"]
            else:
                logger.warning(f"Failed to create entity: {entity.name}")
                return ""
    
    def create_relationship(
        self,
        relationship: Relationship
    ) -> bool:
        """
        Create relationship between entities.
        
        Args:
            relationship: Relationship object
        
        Returns:
            Success status
        """
        with self.driver.session() as session:
            properties = relationship.properties.copy()
            properties["confidence"] = relationship.confidence
            properties["evidence"] = relationship.evidence
            
            # Create relationship
            query = f"""
            MATCH (source:{relationship.source_type.value} {{name: $source_name}})
            MATCH (target:{relationship.target_type.value} {{name: $target_name}})
            MERGE (source)-[r:{relationship.relationship_type.value}]->(target)
            SET r += $properties
            RETURN r
            """
            
            result = session.run(
                query,
                source_name=relationship.source_entity,
                target_name=relationship.target_entity,
                properties=properties
            )
            
            return result.single() is not None
    
    def get_entity_by_name(
        self,
        name: str,
        entity_type: NodeType = None
    ) -> Optional[Dict]:
        """
        Get entity by name.
        
        Args:
            name: Entity name
            entity_type: Optional entity type filter
        
        Returns:
            Entity data or None
        """
        with self.driver.session() as session:
            if entity_type:
                query = f"""
                MATCH (n:{entity_type.value} {{name: $name}})
                RETURN n, elementId(n) as node_id
                """
            else:
                query = """
                MATCH (n {name: $name})
                RETURN n, labels(n) as labels, elementId(n) as node_id
                """
            
            result = session.run(query, name=name)
            record = result.single()
            
            if record:
                node = dict(record["n"])
                node["node_id"] = record["node_id"]
                if not entity_type:
                    node["labels"] = record["labels"]
                return node
            
            return None
    
    def get_related_entities(
        self,
        entity_name: str,
        relationship_types: List[RelationshipType] = None,
        max_depth: int = 1
    ) -> List[Dict]:
        """
        Get entities related to a given entity.
        
        Args:
            entity_name: Source entity name
            relationship_types: Optional filter by relationship types
            max_depth: Maximum traversal depth
        
        Returns:
            List of related entities with relationships
        """
        with self.driver.session() as session:
            if relationship_types:
                rel_filter = "|".join([rt.value for rt in relationship_types])
                query = f"""
                MATCH path = (source {{name: $name}})-[:{rel_filter}*1..{max_depth}]-(target)
                RETURN target, labels(target) as labels, relationships(path) as rels
                """
            else:
                query = f"""
                MATCH path = (source {{name: $name}})-[*1..{max_depth}]-(target)
                RETURN target, labels(target) as labels, relationships(path) as rels
                LIMIT 100
                """
            
            result = session.run(query, name=entity_name)
            
            related = []
            for record in result:
                node = dict(record["target"])
                node["labels"] = record["labels"]
                node["relationships"] = [dict(r) for r in record["rels"]]
                related.append(node)
            
            return related
    
    def link_to_qdrant(
        self,
        entity_name: str,
        entity_type: NodeType,
        qdrant_point_id: str
    ):
        """
        Add Qdrant point ID to entity node.
        
        Args:
            entity_name: Entity name
            entity_type: Entity type
            qdrant_point_id: Qdrant point ID to link
        """
        with self.driver.session() as session:
            query = f"""
            MATCH (n:{entity_type.value} {{name: $name}})
            SET n.qdrant_point_ids = 
                CASE 
                    WHEN n.qdrant_point_ids IS NULL THEN [$point_id]
                    ELSE n.qdrant_point_ids + $point_id
                END
            RETURN n
            """
            
            session.run(
                query,
                name=entity_name,
                point_id=qdrant_point_id
            )
    
    def query_cypher(self, query: str, parameters: Dict = None) -> List[Dict]:
        """
        Execute custom Cypher query.
        
        Args:
            query: Cypher query string
            parameters: Query parameters
        
        Returns:
            Query results
        """
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [dict(record) for record in result]
    
    def get_entity_context(
        self,
        entity_ids: List[str]
    ) -> Dict:
        """
        Get graph context for entities (relationships, neighbors).
        
        Args:
            entity_ids: List of Neo4j node IDs
        
        Returns:
            Context dictionary with entities and relationships
        """
        with self.driver.session() as session:
            # Convert string IDs to proper format
            id_list = ", ".join([f"'{id}'" for id in entity_ids])
            
            query = f"""
            MATCH (n)
            WHERE elementId(n) IN [{id_list}]
            OPTIONAL MATCH (n)-[r]-(related)
            RETURN n, labels(n) as labels, 
                   collect({{rel: r, node: related, labels: labels(related)}}) as relationships
            """
            
            result = session.run(query)
            
            context = {
                "entities": [],
                "relationships": []
            }
            
            for record in result:
                entity = dict(record["n"])
                entity["labels"] = record["labels"]
                context["entities"].append(entity)
                
                for rel_data in record["relationships"]:
                    if rel_data["rel"]:
                        context["relationships"].append({
                            "type": type(rel_data["rel"]).__name__,
                            "properties": dict(rel_data["rel"]),
                            "target": dict(rel_data["node"]),
                            "target_labels": rel_data["labels"]
                        })
            
            return context
