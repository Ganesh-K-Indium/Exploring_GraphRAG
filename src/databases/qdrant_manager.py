"""
Qdrant vector database manager.
Handles multi-vector storage and hybrid search.
"""
from typing import List, Dict, Optional, Union
from loguru import logger
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct,
    SparseVector, NamedSparseVector, SparseVectorParams,
    SparseIndexParams, ScalarQuantization, ScalarQuantizationConfig,
    ScalarType, HnswConfigDiff, OptimizersConfigDiff,
    Filter, FieldCondition, MatchValue
)

from src.config import settings


class QdrantManager:
    """
    Manages Qdrant vector database operations.
    Handles multi-vector storage and hybrid search.
    """
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        api_key: str = None,
        collection_name: str = "10k_filings"
    ):
        """
        Initialize Qdrant manager.
        
        Args:
            host: Qdrant host
            port: Qdrant port
            api_key: Qdrant API key
            collection_name: Collection name
        """
        self.host = host or settings.qdrant_host
        self.port = port or settings.qdrant_port
        self.api_key = api_key or settings.qdrant_api_key
        self.collection_name = collection_name
        
        self.client = QdrantClient(
            host=self.host,
            port=self.port,
            api_key=self.api_key
        )
        
        logger.info(f"QdrantManager initialized for collection: {collection_name}")
    
    def create_collection(
        self,
        dense_dim: int = 1024,
        recreate: bool = False
    ):
        """
        Create Qdrant collection with multi-vector support.
        
        Args:
            dense_dim: Dense vector dimension
            recreate: Whether to recreate if exists
        """
        if recreate:
            self.client.delete_collection(self.collection_name)
            logger.info(f"Deleted existing collection: {self.collection_name}")
        
        # Check if collection exists
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if exists and not recreate:
            logger.info(f"Collection {self.collection_name} already exists")
            return
        
        # Create collection with multi-vector support
        self.client.create_collection(
            collection_name=self.collection_name,
            vectors_config={
                "dense": VectorParams(
                    size=dense_dim,
                    distance=Distance.COSINE
                )
            },
            sparse_vectors_config={
                "sparse": SparseVectorParams(
                    index=SparseIndexParams(
                        on_disk=False
                    )
                )
            },
            quantization_config=ScalarQuantization(
                scalar=ScalarQuantizationConfig(
                    type=ScalarType.INT8,
                    quantile=0.99,
                    always_ram=True
                )
            ),
            hnsw_config=HnswConfigDiff(
                m=16,
                ef_construct=100
            ),
            optimizers_config=OptimizersConfigDiff(
                indexing_threshold=20000
            )
        )
        
        logger.info(f"Created collection: {self.collection_name}")
    
    def upsert_points(
        self,
        points: List[Dict]
    ):
        """
        Upsert points with multi-vector embeddings.
        
        Args:
            points: List of point dictionaries with embeddings and payload
        """
        qdrant_points = []
        
        for i, point in enumerate(points):
            point_id = point.get("id", i)
            dense_vector = point["dense"]
            sparse_vector = point["sparse"]
            payload = point.get("payload", {})
            
            # Add ColBERT vectors to payload (can't store in vector field directly)
            if "colbert" in point:
                payload["colbert_tokens"] = point["colbert"].tolist()
            
            qdrant_point = PointStruct(
                id=point_id,
                vector={
                    "dense": dense_vector
                },
                payload=payload
            )
            
            # Add sparse vector
            if sparse_vector:
                qdrant_point.vector["sparse"] = SparseVector(
                    indices=sparse_vector["indices"],
                    values=sparse_vector["values"]
                )
            
            qdrant_points.append(qdrant_point)
        
        # Upsert in batches
        batch_size = 100
        for i in range(0, len(qdrant_points), batch_size):
            batch = qdrant_points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        
        logger.info(f"Upserted {len(qdrant_points)} points")
    
    def search_dense(
        self,
        query_vector: List[float],
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Dense vector search.
        
        Args:
            query_vector: Dense query vector
            limit: Number of results
            filters: Optional filters
        
        Returns:
            Search results
        """
        filter_obj = self._build_filter(filters) if filters else None
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=("dense", query_vector),
            query_filter=filter_obj,
            limit=limit,
            with_payload=True
        )
        
        return self._format_results(results)
    
    def search_sparse(
        self,
        query_vector: Dict,
        limit: int = 10,
        filters: Optional[Dict] = None
    ) -> List[Dict]:
        """
        Sparse vector search.
        
        Args:
            query_vector: Sparse query vector dict
            limit: Number of results
            filters: Optional filters
        
        Returns:
            Search results
        """
        filter_obj = self._build_filter(filters) if filters else None
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=NamedSparseVector(
                name="sparse",
                vector=SparseVector(
                    indices=query_vector["indices"],
                    values=query_vector["values"]
                )
            ),
            query_filter=filter_obj,
            limit=limit,
            with_payload=True
        )
        
        return self._format_results(results)
    
    def get_points(
        self,
        point_ids: List[Union[str, int]]
    ) -> List[Dict]:
        """
        Retrieve points by IDs.
        
        Args:
            point_ids: List of point IDs
        
        Returns:
            Points data
        """
        results = self.client.retrieve(
            collection_name=self.collection_name,
            ids=point_ids,
            with_payload=True,
            with_vectors=True
        )
        
        return [self._format_point(p) for p in results]
    
    def _build_filter(self, filters: Dict) -> Filter:
        """Build Qdrant filter from dict."""
        conditions = []
        
        for key, value in filters.items():
            conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )
        
        return Filter(must=conditions) if conditions else None
    
    def _format_results(self, results) -> List[Dict]:
        """Format search results."""
        formatted = []
        
        for result in results:
            formatted.append({
                "id": result.id,
                "score": result.score,
                "payload": result.payload
            })
        
        return formatted
    
    def _format_point(self, point) -> Dict:
        """Format single point."""
        return {
            "id": point.id,
            "vector": point.vector,
            "payload": point.payload
        }
    
    def add_neo4j_link(
        self,
        point_id: Union[str, int],
        neo4j_node_id: str
    ):
        """
        Add Neo4j node ID to point payload.
        
        Args:
            point_id: Qdrant point ID
            neo4j_node_id: Neo4j node ID
        """
        point = self.client.retrieve(
            collection_name=self.collection_name,
            ids=[point_id]
        )[0]
        
        payload = point.payload or {}
        
        if "neo4j_node_ids" not in payload:
            payload["neo4j_node_ids"] = []
        
        if neo4j_node_id not in payload["neo4j_node_ids"]:
            payload["neo4j_node_ids"].append(neo4j_node_id)
        
        self.client.set_payload(
            collection_name=self.collection_name,
            payload=payload,
            points=[point_id]
        )
    
    def scroll_all(self, batch_size: int = 100) -> List[Dict]:
        """
        Scroll through all points in collection.
        
        Args:
            batch_size: Batch size for scrolling
        
        Returns:
            All points
        """
        all_points = []
        offset = None
        
        while True:
            results, offset = self.client.scroll(
                collection_name=self.collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=True
            )
            
            all_points.extend([self._format_point(p) for p in results])
            
            if offset is None:
                break
        
        return all_points
