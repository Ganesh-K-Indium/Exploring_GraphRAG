"""
Complete ingestion pipeline for 10-K reports.
Orchestrates extraction, ontology creation, embedding, and storage.
"""
from typing import Dict, List
from pathlib import Path
from loguru import logger
from tqdm import tqdm

from src.extraction import PDFExtractor
from src.ontology import NERExtractor, LLMExtractor, EntityResolver
from src.embeddings import EncoderManager
from src.databases import Neo4jManager, QdrantManager, DatabaseLinker
from src.config import load_yaml_config


class IngestionPipeline:
    """
    Complete ingestion pipeline.
    Processes 10-K PDF through all stages to final storage.
    """
    
    def __init__(
        self,
        neo4j_manager: Neo4jManager,
        qdrant_manager: QdrantManager,
        config_dir: str = "config"
    ):
        """
        Initialize ingestion pipeline.
        
        Args:
            neo4j_manager: Neo4j database manager
            qdrant_manager: Qdrant database manager
            config_dir: Configuration directory path
        """
        self.neo4j = neo4j_manager
        self.qdrant = qdrant_manager
        self.linker = DatabaseLinker(neo4j_manager, qdrant_manager)
        
        # Load configurations
        config_path = Path(config_dir)
        self.extraction_config = load_yaml_config(
            config_path / "extraction_config.yaml"
        )["pdf_extraction"]
        self.model_config = load_yaml_config(
            config_path / "model_config.yaml"
        )
        
        # Initialize components
        logger.info("Initializing pipeline components...")
        
        self.pdf_extractor = PDFExtractor(
            config=self.extraction_config,
            use_vision=True
        )
        
        self.ner_extractor = NERExtractor(
            config=self.model_config["ner"]
        )
        
        self.llm_extractor = LLMExtractor(
            config=self.model_config["llm"]
        )
        
        self.entity_resolver = EntityResolver()
        
        self.encoder_manager = EncoderManager(
            config=self.model_config["embeddings"]
        )
        
        logger.info("IngestionPipeline initialized")
    
    def ingest_document(
        self,
        pdf_path: str,
        metadata: Dict = None
    ) -> Dict:
        """
        Ingest a 10-K document through complete pipeline.
        
        Args:
            pdf_path: Path to PDF file
            metadata: Document metadata (ticker, filing_date, etc.)
        
        Returns:
            Ingestion result summary
        """
        logger.info(f"Starting ingestion: {pdf_path}")
        
        # Phase 1: Multimodal extraction
        logger.info("Phase 1: Extracting content from PDF...")
        extraction_result = self.pdf_extractor.extract_from_pdf(
            pdf_path,
            metadata
        )
        
        # Phase 2: Entity and relationship extraction
        logger.info("Phase 2: Extracting entities and relationships...")
        ontology_result = self._extract_ontology(
            extraction_result["chunks"],
            metadata
        )
        
        # Phase 3: Embedding
        logger.info("Phase 3: Generating embeddings...")
        embeddings_result = self._generate_embeddings(
            extraction_result["chunks"]
        )
        
        # Phase 4: Storage
        logger.info("Phase 4: Storing in databases...")
        storage_result = self._store_data(
            extraction_result["chunks"],
            embeddings_result,
            ontology_result,
            metadata
        )
        
        logger.info("Ingestion complete!")
        
        return {
            "document_id": extraction_result["document_id"],
            "file_name": extraction_result["file_name"],
            "metadata": metadata,
            "stats": {
                "num_chunks": len(extraction_result["chunks"]),
                "num_entities": len(ontology_result["entities"]),
                "num_relationships": len(ontology_result["relationships"]),
                "num_embeddings": len(embeddings_result)
            },
            "extraction": extraction_result["stats"],
            "storage": storage_result
        }
    
    def _extract_ontology(
        self,
        chunks: List[Dict],
        metadata: Dict
    ) -> Dict:
        """Extract entities and relationships from chunks."""
        all_entities = []
        all_relationships = []
        
        for chunk in tqdm(chunks, desc="Extracting ontology"):
            chunk_id = chunk["chunk_id"]
            text = chunk["text_content"]
            
            # NER extraction
            entities = self.ner_extractor.extract_entities(text, chunk_id)
            
            # Extract from tables if present
            if chunk.get("table_data"):
                table_entities = self.ner_extractor.extract_from_table(
                    {
                        "table_id": chunk_id,
                        "columns": [],  # Would need to extract from table_data
                        "data": chunk["table_data"]
                    }
                )
                entities.extend(table_entities)
            
            all_entities.extend(entities)
            
            # LLM relationship extraction (for text chunks with entities)
            if entities and len(text) > 100:
                relationships = self.llm_extractor.extract_relationships(
                    text,
                    [e.to_dict() for e in entities],
                    chunk_id
                )
                all_relationships.extend(relationships)
        
        # Resolve entities
        resolved_entities = self.entity_resolver.resolve_entities(all_entities)
        
        return {
            "entities": resolved_entities,
            "relationships": all_relationships
        }
    
    def _generate_embeddings(self, chunks: List[Dict]) -> List[Dict]:
        """Generate multi-vector embeddings for chunks."""
        embeddings = []
        
        # Batch process chunks
        texts = [chunk["text_content"] for chunk in chunks]
        
        logger.info(f"Encoding {len(texts)} chunks...")
        embedded_chunks = self.encoder_manager.encode_documents(texts)
        
        # Combine with original chunk data
        for chunk, emb in zip(chunks, embedded_chunks):
            embeddings.append({
                "chunk": chunk,
                "dense": emb["dense"],
                "sparse": emb["sparse"],
                "colbert": emb["colbert"]
            })
        
        return embeddings
    
    def _store_data(
        self,
        chunks: List[Dict],
        embeddings: List[Dict],
        ontology: Dict,
        metadata: Dict
    ) -> Dict:
        """Store data in Neo4j and Qdrant."""
        # Store entities in Neo4j
        logger.info("Storing entities in Neo4j...")
        entity_node_ids = {}
        
        for entity in tqdm(ontology["entities"], desc="Creating entities"):
            node_id = self.neo4j.create_entity(entity)
            entity_node_ids[entity.name] = node_id
        
        # Store relationships in Neo4j
        logger.info("Storing relationships in Neo4j...")
        rel_count = 0
        for relationship in tqdm(ontology["relationships"], desc="Creating relationships"):
            success = self.neo4j.create_relationship(relationship)
            if success:
                rel_count += 1
        
        # Prepare Qdrant points
        logger.info("Storing embeddings in Qdrant...")
        qdrant_points = []
        
        for i, emb_data in enumerate(embeddings):
            chunk = emb_data["chunk"]
            
            # Get entity IDs for this chunk
            chunk_entities = chunk.get("metadata", {}).get("entities", [])
            neo4j_ids = [
                entity_node_ids.get(ent, "")
                for ent in chunk_entities
                if ent in entity_node_ids
            ]
            
            point = {
                "id": i,
                "dense": emb_data["dense"],
                "sparse": emb_data["sparse"],
                "colbert": emb_data["colbert"],
                "payload": {
                    "chunk_id": chunk["chunk_id"],
                    "text": chunk["text_content"],
                    "chunk_type": chunk["chunk_type"],
                    "section": chunk.get("metadata", {}).get("section", ""),
                    "page_numbers": chunk.get("metadata", {}).get("page_numbers", []),
                    "company_ticker": metadata.get("ticker", ""),
                    "filing_date": metadata.get("filing_date", ""),
                    "fiscal_year": metadata.get("fiscal_year", ""),
                    "has_table": chunk.get("table_data") is not None,
                    "has_chart": chunk.get("image_data") is not None,
                    "neo4j_node_ids": neo4j_ids,
                    "entities": chunk_entities,
                    "table_data": chunk.get("table_data"),
                    "image_data": chunk.get("image_data")
                }
            }
            
            qdrant_points.append(point)
        
        # Upsert to Qdrant
        self.qdrant.upsert_points(qdrant_points)
        
        return {
            "entities_stored": len(entity_node_ids),
            "relationships_stored": rel_count,
            "embeddings_stored": len(qdrant_points)
        }
    
    def batch_ingest(
        self,
        pdf_paths: List[str],
        metadata_list: List[Dict] = None
    ) -> List[Dict]:
        """
        Ingest multiple documents.
        
        Args:
            pdf_paths: List of PDF file paths
            metadata_list: List of metadata dictionaries
        
        Returns:
            List of ingestion results
        """
        if metadata_list is None:
            metadata_list = [{}] * len(pdf_paths)
        
        results = []
        
        for pdf_path, metadata in zip(pdf_paths, metadata_list):
            try:
                result = self.ingest_document(pdf_path, metadata)
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to ingest {pdf_path}: {e}")
                results.append({
                    "file_name": pdf_path,
                    "error": str(e)
                })
        
        return results
