"""
Dense embedding using Voyage AI or OpenAI.
Semantic embeddings for similarity search.
"""
from typing import List, Union
import hashlib
from loguru import logger

from src.config import settings


class DenseEmbedder:
    """
    Dense embedding encoder.
    Supports Voyage AI (financial) and OpenAI embeddings.
    """
    
    def __init__(self, config: dict = None):
        """
        Initialize dense embedder.
        
        Args:
            config: Embedding configuration
        """
        self.config = config or {}
        self.model = self.config.get("model", settings.dense_embedding_model)
        self.dimension = self.config.get("dimension", 1024)
        self.batch_size = self.config.get("batch_size", 64)
        
        # Initialize client based on model
        if "voyage" in self.model.lower():
            self.provider = "voyage"
            self._init_voyage()
        elif "text-embedding" in self.model.lower():
            self.provider = "openai"
            self._init_openai()
        else:
            # Fallback to sentence transformers
            self.provider = "sentence_transformers"
            self._init_sentence_transformers()
        
        # Cache for embeddings
        self.cache = {} if self.config.get("cache_enabled", True) else None
        self.cache_size = self.config.get("cache_size", 1000)
        
        logger.info(f"DenseEmbedder initialized with {self.provider} ({self.model})")
    
    def _init_voyage(self):
        """Initialize Voyage AI client."""
        try:
            import voyageai
            self.client = voyageai.Client(api_key=settings.voyage_api_key)
        except ImportError:
            logger.error("voyageai not installed. Install with: pip install voyageai")
            raise
    
    def _init_openai(self):
        """Initialize OpenAI client."""
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=settings.openai_api_key)
        except ImportError:
            logger.error("openai not installed. Install with: pip install openai")
            raise
    
    def _init_sentence_transformers(self):
        """Initialize sentence transformers model."""
        try:
            from sentence_transformers import SentenceTransformer
            self.model_obj = SentenceTransformer(self.model)
            self.dimension = self.model_obj.get_sentence_embedding_dimension()
        except ImportError:
            logger.error("sentence-transformers not installed")
            raise
    
    def encode(
        self,
        texts: Union[str, List[str]],
        input_type: str = "document"
    ) -> Union[List[float], List[List[float]]]:
        """
        Encode text(s) to dense embeddings.
        
        Args:
            texts: Single text or list of texts
            input_type: "document" or "query"
        
        Returns:
            Embedding(s) as list(s) of floats
        """
        # Handle single text
        single_input = isinstance(texts, str)
        if single_input:
            texts = [texts]
        
        # Check cache
        embeddings = []
        texts_to_encode = []
        indices_to_encode = []
        
        if self.cache is not None:
            for i, text in enumerate(texts):
                cache_key = self._get_cache_key(text, input_type)
                if cache_key in self.cache:
                    embeddings.append(self.cache[cache_key])
                else:
                    embeddings.append(None)
                    texts_to_encode.append(text)
                    indices_to_encode.append(i)
        else:
            texts_to_encode = texts
            indices_to_encode = list(range(len(texts)))
        
        # Encode uncached texts
        if texts_to_encode:
            new_embeddings = self._encode_batch(texts_to_encode, input_type)
            
            # Update cache and results
            for idx, emb in zip(indices_to_encode, new_embeddings):
                embeddings[idx] = emb
                if self.cache is not None:
                    cache_key = self._get_cache_key(texts[idx], input_type)
                    self._add_to_cache(cache_key, emb)
        
        return embeddings[0] if single_input else embeddings
    
    def _encode_batch(
        self,
        texts: List[str],
        input_type: str
    ) -> List[List[float]]:
        """Encode batch of texts."""
        if self.provider == "voyage":
            return self._encode_voyage(texts, input_type)
        elif self.provider == "openai":
            return self._encode_openai(texts)
        else:
            return self._encode_sentence_transformers(texts)
    
    def _encode_voyage(
        self,
        texts: List[str],
        input_type: str
    ) -> List[List[float]]:
        """Encode using Voyage AI."""
        try:
            result = self.client.embed(
                texts=texts,
                model=self.model,
                input_type=input_type
            )
            return result.embeddings
        except Exception as e:
            logger.error(f"Voyage encoding failed: {e}")
            raise
    
    def _encode_openai(self, texts: List[str]) -> List[List[float]]:
        """Encode using OpenAI with automatic batching for token limits."""
        import tiktoken
        
        try:
            # Get encoding for token counting
            encoding = tiktoken.encoding_for_model("gpt-4o")
            
            # OpenAI embedding limit is 8191 tokens per request
            max_tokens = 8000  # Safety margin
            embeddings = []
            current_batch = []
            current_tokens = 0
            
            for text in texts:
                # Count tokens in text
                text_tokens = len(encoding.encode(text[:30000]))  # Limit text length
                
                # If single text exceeds limit, truncate it
                if text_tokens > max_tokens:
                    logger.warning(f"Text exceeds token limit ({text_tokens} tokens), truncating")
                    # Truncate to max tokens
                    tokens = encoding.encode(text)[:max_tokens]
                    text = encoding.decode(tokens)
                    text_tokens = max_tokens
                
                # Check if adding this text would exceed batch limit
                if current_tokens + text_tokens > max_tokens and current_batch:
                    # Process current batch
                    response = self.client.embeddings.create(
                        input=current_batch,
                        model=self.model
                    )
                    embeddings.extend([item.embedding for item in response.data])
                    current_batch = []
                    current_tokens = 0
                
                current_batch.append(text)
                current_tokens += text_tokens
            
            # Process remaining batch
            if current_batch:
                response = self.client.embeddings.create(
                    input=current_batch,
                    model=self.model
                )
                embeddings.extend([item.embedding for item in response.data])
            
            return embeddings
            
        except Exception as e:
            logger.error(f"OpenAI encoding failed: {e}")
            raise
    
    def _encode_sentence_transformers(
        self,
        texts: List[str]
    ) -> List[List[float]]:
        """Encode using sentence transformers."""
        embeddings = self.model_obj.encode(
            texts,
            batch_size=self.batch_size,
            show_progress_bar=False
        )
        return embeddings.tolist()
    
    def _get_cache_key(self, text: str, input_type: str) -> str:
        """Generate cache key for text."""
        combined = f"{text}:{input_type}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def _add_to_cache(self, key: str, embedding: List[float]):
        """Add embedding to cache."""
        if len(self.cache) >= self.cache_size:
            # Remove oldest entry (FIFO)
            self.cache.pop(next(iter(self.cache)))
        self.cache[key] = embedding
