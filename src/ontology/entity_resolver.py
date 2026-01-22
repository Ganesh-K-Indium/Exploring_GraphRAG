"""
Entity resolution and deduplication.
Merges similar entities and resolves aliases.
"""
from typing import List, Dict, Tuple
from loguru import logger
from difflib import SequenceMatcher

from .schema import Entity


class EntityResolver:
    """
    Resolves and deduplicates entities.
    Handles entity linking and alias resolution.
    """
    
    def __init__(self, similarity_threshold: float = 0.85):
        """
        Initialize entity resolver.
        
        Args:
            similarity_threshold: Minimum similarity for entity matching
        """
        self.similarity_threshold = similarity_threshold
        self.entity_cache: Dict[str, Entity] = {}
        
        logger.info("EntityResolver initialized")
    
    def resolve_entities(self, entities: List[Entity]) -> List[Entity]:
        """
        Resolve and deduplicate entities.
        
        Args:
            entities: List of extracted entities
        
        Returns:
            List of resolved entities
        """
        if not entities:
            return []
        
        # Group by entity type
        grouped = {}
        for entity in entities:
            ent_type = entity.entity_type
            if ent_type not in grouped:
                grouped[ent_type] = []
            grouped[ent_type].append(entity)
        
        # Resolve within each group
        resolved = []
        for ent_type, ent_list in grouped.items():
            resolved.extend(self._resolve_group(ent_list))
        
        logger.info(f"Resolved {len(entities)} entities to {len(resolved)} unique entities")
        return resolved
    
    def _resolve_group(self, entities: List[Entity]) -> List[Entity]:
        """Resolve entities within same type."""
        if len(entities) <= 1:
            return entities
        
        # Build similarity graph
        clusters = []
        used = set()
        
        for i, entity in enumerate(entities):
            if i in used:
                continue
            
            cluster = [entity]
            used.add(i)
            
            # Find similar entities
            for j, other in enumerate(entities[i+1:], start=i+1):
                if j in used:
                    continue
                
                if self._are_similar(entity, other):
                    cluster.append(other)
                    used.add(j)
            
            clusters.append(cluster)
        
        # Merge each cluster
        resolved = []
        for cluster in clusters:
            merged = self._merge_entities(cluster)
            resolved.append(merged)
        
        return resolved
    
    def _are_similar(self, entity1: Entity, entity2: Entity) -> bool:
        """Check if two entities are similar."""
        if entity1.entity_type != entity2.entity_type:
            return False
        
        # Normalize names
        name1 = self._normalize_name(entity1.name)
        name2 = self._normalize_name(entity2.name)
        
        # Calculate similarity
        similarity = SequenceMatcher(None, name1, name2).ratio()
        
        return similarity >= self.similarity_threshold
    
    def _normalize_name(self, name: str) -> str:
        """Normalize entity name for comparison."""
        # Convert to lowercase
        name = name.lower()
        
        # Remove common suffixes
        suffixes = [" inc", " inc.", " corp", " corp.", " ltd", " llc", " co", " co."]
        for suffix in suffixes:
            if name.endswith(suffix):
                name = name[:-len(suffix)]
        
        # Remove punctuation and extra whitespace
        import string
        name = name.translate(str.maketrans("", "", string.punctuation))
        name = " ".join(name.split())
        
        return name
    
    def _merge_entities(self, entities: List[Entity]) -> Entity:
        """Merge multiple entities into one."""
        if len(entities) == 1:
            return entities[0]
        
        # Use entity with highest confidence as base
        base = max(entities, key=lambda e: e.confidence)
        
        # Merge properties
        merged_properties = {}
        for entity in entities:
            merged_properties.update(entity.properties)
        
        # Collect all source chunk IDs
        source_chunks = [e.source_chunk_id for e in entities if e.source_chunk_id]
        merged_properties["all_source_chunks"] = source_chunks
        
        # Average confidence
        avg_confidence = sum(e.confidence for e in entities) / len(entities)
        
        merged = Entity(
            name=base.name,
            entity_type=base.entity_type,
            properties=merged_properties,
            confidence=avg_confidence,
            source_chunk_id=base.source_chunk_id
        )
        
        return merged
    
    def link_entity(self, entity: Entity) -> str:
        """
        Link entity to canonical form and return ID.
        
        Args:
            entity: Entity to link
        
        Returns:
            Canonical entity ID
        """
        # Create cache key
        cache_key = f"{entity.entity_type}:{self._normalize_name(entity.name)}"
        
        if cache_key in self.entity_cache:
            # Return existing entity ID
            cached = self.entity_cache[cache_key]
            return cached.properties.get("entity_id", cache_key)
        else:
            # New entity - assign ID
            entity_id = f"{entity.entity_type.value}_{len(self.entity_cache)}"
            entity.properties["entity_id"] = entity_id
            self.entity_cache[cache_key] = entity
            return entity_id
