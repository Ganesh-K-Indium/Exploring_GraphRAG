"""
RAG generator using GPT-4o.
Generates answers with citations from multimodal context.
"""
from typing import Dict, List
from loguru import logger
from openai import OpenAI

from src.config import settings
from .context_builder import ContextBuilder


class RAGGenerator:
    """
    RAG-based answer generation using GPT-4o.
    Generates answers with proper citations from multimodal context.
    """
    
    def __init__(
        self,
        api_key: str = None,
        model: str = None,
        config: Dict = None
    ):
        """
        Initialize RAG generator.
        
        Args:
            api_key: OpenAI API key
            model: GPT model name
            config: Generator configuration
        """
        self.client = OpenAI(
            api_key=api_key or settings.openai_api_key
        )
        self.model = model or settings.llm_model
        self.config = config or {}
        
        self.max_tokens = self.config.get("max_tokens", 4096)
        self.temperature = self.config.get("temperature", 0.0)
        
        self.context_builder = ContextBuilder(config)
        
        self.system_prompt = self._get_system_prompt()
        
        logger.info(f"RAGGenerator initialized with {self.model}")
        
        # Note: OpenAI doesn't use system prompts the same way, we'll include it in messages
    
    def generate(
        self,
        query: str,
        search_results: List[Dict],
        graph_context: Dict = None
    ) -> Dict:
        """
        Generate answer from search results.
        
        Args:
            query: User query
            search_results: Results from hybrid search
            graph_context: Optional graph context
        
        Returns:
            Dictionary with answer and metadata
        """
        logger.info(f"Generating answer for: '{query}'")
        
        # Build context
        context = self.context_builder.build_context(
            query,
            search_results,
            graph_context
        )
        
        # Format context for LLM
        context_str = self.context_builder.format_for_llm(context)
        
        # Create prompt
        user_prompt = self._create_prompt(query, context_str)
        
        # Generate with GPT-4o
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=self.max_tokens,
                temperature=self.temperature,
                messages=[
                    {
                        "role": "system",
                        "content": self.system_prompt
                    },
                    {
                        "role": "user",
                        "content": user_prompt
                    }
                ]
            )
            
            answer = response.choices[0].message.content
            
            return {
                "answer": answer,
                "query": query,
                "context": context,
                "sources": context["sources"],
                "model": self.model,
                "usage": {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens
                }
            }
        
        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return {
                "answer": f"Error generating answer: {str(e)}",
                "query": query,
                "error": str(e)
            }
    
    def _get_system_prompt(self) -> str:
        """Get system prompt for Claude."""
        return """You are a financial analyst assistant with deep expertise in analyzing SEC 10-K filings.

Your role is to:
1. Answer questions based ONLY on the provided context from 10-K reports
2. Provide accurate, precise information with proper citations
3. Highlight relevant data from tables and charts when applicable
4. Explain complex financial concepts clearly
5. Indicate when information is insufficient or missing

Citation Format:
- Use [Source] notation for citations (e.g., [AAPL 10-K (2024-10-31), Item 7, Page 45])
- When referencing tables, mention them explicitly (e.g., "According to Table 1...")
- When referencing charts, describe the visual data (e.g., "The revenue trend chart shows...")

Financial Data Guidelines:
- Always include units (millions, billions, etc.)
- Specify time periods (Q1 2024, FY 2023, etc.)
- Note year-over-year changes when available
- Highlight any qualifications or footnotes

If the provided context doesn't contain enough information to answer the question fully, state what's missing and what you can answer."""
    
    def _create_prompt(self, query: str, context: str) -> str:
        """Create user prompt with query and context."""
        return f"""User Query: {query}

Context from 10-K Reports:

{context}

Instructions:
1. Answer the question based on the provided context
2. Cite all sources using [Source] notation
3. For financial data, include units and time periods
4. Reference tables and charts explicitly when using them
5. If data is missing or insufficient, clearly state what's unavailable

Please provide a comprehensive answer:"""
    
    def generate_streaming(
        self,
        query: str,
        search_results: List[Dict],
        graph_context: Dict = None
    ):
        """
        Generate answer with streaming (for UI responsiveness).
        
        Yields chunks of the response as they're generated.
        
        Args:
            query: User query
            search_results: Results from hybrid search
            graph_context: Optional graph context
        
        Yields:
            Response chunks
        """
        # Build context
        context = self.context_builder.build_context(
            query,
            search_results,
            graph_context
        )
        
        context_str = self.context_builder.format_for_llm(context)
        user_prompt = self._create_prompt(query, context_str)
        
        # Stream response
        stream = self.client.chat.completions.create(
            model=self.model,
            max_tokens=self.max_tokens,
            temperature=self.temperature,
            messages=[
                {
                    "role": "system",
                    "content": self.system_prompt
                },
                {
                    "role": "user",
                    "content": user_prompt
                }
            ],
            stream=True
        )
        
        for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content
