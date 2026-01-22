"""
Database linker for bidirectional linking between Neo4j and Qdrant.
"""
from typing import List, Dict
from loguru import logger

from .neo4j_manager import Neo4jManager
from .qdrant_manager import QdrantManager
from src.ontology.schema import Entity, NodeType


class DatabaseLinker:
    """
    Links Neo4j graph database with Qdrant vector database.
    Maintains bidirectional references between entities and embeddings.
    """
    
    def __init__(
        self,
        neo4j_manager: Neo4jManager,
        qdrant_manager: QdrantManager
    ):
        """
        Initialize database linker.
        
        Args:
            neo4j_manager: Neo4j manager instance
            qdrant_manager: Qdrant manager instance
        """
        self.neo4j = neo4j_manager
        self.qdrant = qdrant_manager
        
        logger.info("DatabaseLinker initialized")
    
    def link_chunk_to_entities(
        self,
        chunk: Dict,
        entities: List[Entity],
        qdrant_point_id: str
    ) -> Dict[str, str]:
        """
        Link a chunk to its entities in both databases.
        
        Args:
            chunk: Chunk data
            entities: Extracted entities
            qdrant_point_id: Qdrant point ID for the chunk
        
        Returns:
            Mapping of entity names to Neo4j node IDs
        """
        entity_node_ids = {}
        
        for entity in entities:
            # Create entity in Neo4j with Qdrant link
            node_id = self.neo4j.create_entity(entity, qdrant_point_id)
            entity_node_ids[entity.name] = node_id
        
        # Update Qdrant payload with Neo4j node IDs
        if entity_node_ids:
            self.qdrant.add_neo4j_link(
                qdrant_point_id,
                list(entity_node_ids.values())[0]  # Link to first entity
            )
        
        return entity_node_ids
    
    def get_enriched_chunks(
        self,
        qdrant_results: List[Dict]
    ) -> List[Dict]:
        """
        Enrich Qdrant search results with Neo4j graph context.
        
        Args:
            qdrant_results: Results from Qdrant search
        
        Returns:
            Enriched results with graph context
        """
        enriched = []
        
        for result in qdrant_results:
            payload = result.get("payload", {})
            neo4j_node_ids = payload.get("neo4j_node_ids", [])
            
            if neo4j_node_ids:
                # Get graph context
                graph_context = self.neo4j.get_entity_context(neo4j_node_ids)
                result["graph_context"] = graph_context
            else:
                result["graph_context"] = {"entities": [], "relationships": []}
            
            enriched.append(result)
        
        return enriched
    
    def get_entity_chunks(
        self,
        entity_name: str,
        entity_type: NodeType
    ) -> List[Dict]:
        """
        Get all chunks that mention a specific entity.
        
        Args:
            entity_name: Entity name
            entity_type: Entity type
        
        Returns:
            List of chunks from Qdrant
        """
        # Get entity from Neo4j
        entity = self.neo4j.get_entity_by_name(entity_name, entity_type)
        
        if not entity:
            logger.warning(f"Entity not found: {entity_name}")
            return []
        
        # Get Qdrant point IDs
        qdrant_point_ids = entity.get("qdrant_point_ids", [])
        
        if not qdrant_point_ids:
            return []
        
        # Retrieve chunks from Qdrant
        chunks = self.qdrant.get_points(qdrant_point_ids)
        
        return chunks
    
    def cross_search(
        self,
        query: str,
        query_embeddings: Dict,
        entity_filter: List[str] = None,
        limit: int = 10
    ) -> List[Dict]:
        """
        Perform cross-database search.
        
        1. Vector search in Qdrant
        2. Extract entities from results
        3. Graph traversal in Neo4j
        4. Enrich results with graph context
        
        Args:
            query: Query text
            query_embeddings: Query embeddings (dense, sparse, colbert)
            entity_filter: Optional entity names to filter by
            limit: Number of results
        
        Returns:
            Enriched search results
        """
        # Vector search in Qdrant
        dense_results = self.qdrant.search_dense(
            query_embeddings["dense"],
            limit=limit * 2  # Get more for fusion
        )
        
        # Get entity IDs from results
        entity_ids = set()
        for result in dense_results:
            payload = result.get("payload", {})
            neo4j_ids = payload.get("neo4j_node_ids", [])
            entity_ids.update(neo4j_ids)
        
        # Graph traversal for related entities
        if entity_ids:
            graph_context = self.neo4j.get_entity_context(list(entity_ids))
        else:
            graph_context = {"entities": [], "relationships": []}
        
        # Enrich results
        for result in dense_results[:limit]:
            result["graph_context"] = graph_context
        
        return dense_results[:limit]
    
    def create_section_node(
        self,
        section_name: str,
        section_data: Dict,
        document_id: str
    ) -> str:
        """
        Create a section node in Neo4j for document structure.
        
        Args:
            section_name: Section name (e.g., "Item_7_MD&A")
            section_data: Section metadata
            document_id: Document ID
        
        Returns:
            Neo4j node ID
        """
        with self.neo4j.driver.session() as session:
            query = """
            MERGE (s:Section {name: $name, document_id: $doc_id})
            SET s += $properties
            RETURN elementId(s) as node_id
            """
            
            result = session.run(
                query,
                name=section_name,
                doc_id=document_id,
                properties=section_data
            )
            
            record = result.single()
            return record["node_id"] if record else ""
