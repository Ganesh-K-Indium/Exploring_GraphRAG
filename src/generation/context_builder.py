"""
Context builder for multimodal RAG.
Prepares text, tables, charts, and graph context for generation.
"""
from typing import List, Dict
import json
from loguru import logger


class ContextBuilder:
    """
    Builds multimodal context from search results.
    Formats text, tables, charts, and graph data for LLM.
    """
    
    def __init__(self, config: Dict = None):
        """
        Initialize context builder.
        
        Args:
            config: Configuration options
        """
        self.config = config or {}
        self.max_context_length = self.config.get("max_context_length", 15000)
        
        logger.info("ContextBuilder initialized")
    
    def build_context(
        self,
        query: str,
        search_results: List[Dict],
        graph_context: Dict = None
    ) -> Dict:
        """
        Build complete context from search results.
        
        Args:
            query: User query
            search_results: Results from hybrid search
            graph_context: Optional graph context
        
        Returns:
            Structured context dictionary
        """
        context = {
            "query": query,
            "text_chunks": [],
            "tables": [],
            "charts": [],
            "graph_context": [],
            "sources": []
        }
        
        # Process each result
        for result in search_results:
            payload = result.get("payload", {})
            chunk_type = payload.get("chunk_type", "text")
            
            # Extract source information
            source = self._extract_source(payload)
            
            if chunk_type == "text":
                context["text_chunks"].append({
                    "text": payload.get("text_content", ""),
                    "section": payload.get("section", "Unknown"),
                    "source": source,
                    "score": result.get("score", 0.0)
                })
            
            elif chunk_type == "table":
                table_data = payload.get("table_data")
                if table_data:
                    context["tables"].append({
                        "data": table_data,
                        "description": payload.get("text_content", ""),
                        "source": source,
                        "score": result.get("score", 0.0)
                    })
            
            elif chunk_type == "image":
                image_data = payload.get("image_data")
                if image_data:
                    context["charts"].append({
                        "description": image_data.get("description", ""),
                        "insights": image_data.get("insights", []),
                        "chart_type": payload.get("metadata", {}).get("chart_type", "unknown"),
                        "source": source,
                        "score": result.get("score", 0.0)
                    })
            
            # Collect unique sources
            if source not in context["sources"]:
                context["sources"].append(source)
        
        # Add graph context
        if graph_context:
            context["graph_context"] = self._format_graph_context(graph_context)
        
        # Truncate if needed
        context = self._truncate_context(context)
        
        return context
    
    def _extract_source(self, payload: Dict) -> str:
        """Extract source citation from payload."""
        company = payload.get("company_ticker", "Unknown")
        filing_date = payload.get("filing_date", "N/A")
        section = payload.get("section", "Unknown")
        pages = payload.get("page_numbers", [])
        
        page_str = f"Page {pages[0]}" if pages else "Page N/A"
        
        return f"{company} 10-K ({filing_date}), {section}, {page_str}"
    
    def _format_graph_context(self, graph_context: Dict) -> List[str]:
        """Format graph context as readable strings."""
        formatted = []
        
        # Format entities
        entities = graph_context.get("entities", [])
        if entities:
            formatted.append("Related Entities:")
            for entity in entities[:5]:  # Limit to top 5
                labels = entity.get("labels", [])
                name = entity.get("name", "Unknown")
                formatted.append(f"  - {name} ({', '.join(labels)})")
        
        # Format relationships
        relationships = graph_context.get("relationships", [])
        if relationships:
            formatted.append("\nRelationships:")
            for rel in relationships[:10]:  # Limit to top 10
                rel_type = rel.get("type", "RELATED_TO")
                target = rel.get("target", {})
                target_name = target.get("name", "Unknown")
                formatted.append(f"  - {rel_type} → {target_name}")
        
        return formatted
    
    def _truncate_context(self, context: Dict) -> Dict:
        """Truncate context to fit within max length."""
        # Simple character-based truncation
        # In production, use token-based truncation with tiktoken
        
        total_length = 0
        
        # Count text chunks
        for i, chunk in enumerate(context["text_chunks"]):
            chunk_len = len(chunk["text"])
            if total_length + chunk_len > self.max_context_length:
                context["text_chunks"] = context["text_chunks"][:i]
                break
            total_length += chunk_len
        
        return context
    
    def format_for_llm(self, context: Dict) -> str:
        """
        Format context as string for LLM prompt.
        
        Args:
            context: Context dictionary
        
        Returns:
            Formatted context string
        """
        sections = []
        
        # Text excerpts
        if context["text_chunks"]:
            sections.append("=== TEXT EXCERPTS ===\n")
            for i, chunk in enumerate(context["text_chunks"], 1):
                sections.append(
                    f"[{i}] {chunk['section']} (Score: {chunk['score']:.3f})\n"
                    f"{chunk['text']}\n"
                    f"Source: {chunk['source']}\n"
                )
        
        # Tables
        if context["tables"]:
            sections.append("\n=== FINANCIAL TABLES ===\n")
            for i, table in enumerate(context["tables"], 1):
                sections.append(
                    f"[Table {i}] {table['description']}\n"
                    f"Data: {json.dumps(table['data'][:3], indent=2)}...\n"
                    f"Source: {table['source']}\n"
                )
        
        # Charts
        if context["charts"]:
            sections.append("\n=== CHARTS & VISUALIZATIONS ===\n")
            for i, chart in enumerate(context["charts"], 1):
                insights_str = ", ".join(chart["insights"])
                sections.append(
                    f"[Chart {i}] {chart['chart_type']}\n"
                    f"Description: {chart['description']}\n"
                    f"Insights: {insights_str}\n"
                    f"Source: {chart['source']}\n"
                )
        
        # Graph context
        if context["graph_context"]:
            sections.append("\n=== ENTITY RELATIONSHIPS ===\n")
            sections.append("\n".join(context["graph_context"]))
        
        return "\n".join(sections)
