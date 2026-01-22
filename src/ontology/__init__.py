"""
Ontology creation module.
Extracts entities and relationships using NER and LLM.
"""

from .ner_extractor import NERExtractor
from .llm_extractor import LLMExtractor
from .entity_resolver import EntityResolver
from .schema import GraphSchema

__all__ = [
    "NERExtractor",
    "LLMExtractor",
    "EntityResolver",
    "GraphSchema",
]
