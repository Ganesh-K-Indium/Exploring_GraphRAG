"""
Table extraction from PDFs using pdfplumber.
Converts tables to structured format with descriptions.
"""
from typing import Dict, List, Optional
import pandas as pd
from pathlib import Path
from loguru import logger
import pdfplumber


class TableProcessor:
    """
    Extracts tables from PDF documents.
    Generates both structured data and text descriptions.
    """
    
    def __init__(self, config: Dict):
        """
        Initialize table processor.
        
        Args:
            config: Table extraction configuration
        """
        self.config = config
        self.min_rows = config.get("min_rows", 2)
        self.min_cols = config.get("min_cols", 2)
        self.generate_descriptions = config.get("generate_descriptions", True)
        
        logger.info("TableProcessor initialized")
    
    def extract_tables(self, pdf_path: str) -> List[Dict]:
        """
        Extract all tables from PDF.
        
        Args:
            pdf_path: Path to PDF file
        
        Returns:
            List of table dictionaries with data and descriptions
        """
        logger.info(f"Extracting tables from {pdf_path}")
        
        tables = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_num = page.page_number
                    
                    # Extract tables from page
                    page_tables = page.extract_tables()
                    
                    for table_idx, table_data in enumerate(page_tables):
                        if not table_data or len(table_data) < self.min_rows:
                            continue
                        
                        # Convert to DataFrame
                        try:
                            df = pd.DataFrame(table_data[1:], columns=table_data[0])
                            
                            if len(df.columns) < self.min_cols:
                                continue
                            
                            # Clean DataFrame
                            df = self._clean_table(df)
                            
                            # Generate description
                            description = ""
                            if self.generate_descriptions:
                                description = self._generate_table_description(df)
                            
                            # Handle duplicate columns
                            df_cols = df.columns.tolist()
                            if len(df_cols) != len(set(df_cols)):
                                # Make columns unique
                                df.columns = [f"{col}_{i}" if df_cols.count(col) > 1 else col 
                                            for i, col in enumerate(df_cols)]
                            
                            table_dict = {
                                "table_id": f"page{page_num}_table{table_idx}",
                                "page": page_num,
                                "data": df.to_dict(orient="records"),
                                "columns": df.columns.tolist(),
                                "num_rows": len(df),
                                "num_cols": len(df.columns),
                                "description": description,
                                "raw_data": table_data
                            }
                            
                            tables.append(table_dict)
                        
                        except Exception as e:
                            logger.warning(f"Failed to process table on page {page_num}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to extract tables: {e}")
        
        logger.info(f"Extracted {len(tables)} tables")
        return tables
    
    def _clean_table(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and standardize table data."""
        # Remove completely empty rows/columns
        df = df.dropna(how="all", axis=0)
        df = df.dropna(how="all", axis=1)
        
        # Clean column names
        df.columns = [str(col).strip() if col else f"col_{i}" 
                     for i, col in enumerate(df.columns)]
        
        # Fill NaN with empty string
        df = df.fillna("")
        
        # Strip whitespace from string columns
        for col in df.columns:
            try:
                col_dtype = str(df[col].dtype)
                if col_dtype == 'object':
                    df[col] = df[col].astype(str).str.strip()
            except Exception:
                continue
        
        return df
    
    def _generate_table_description(self, df: pd.DataFrame) -> str:
        """
        Generate a textual description of the table.
        This description will be embedded for semantic search.
        
        Args:
            df: Table as DataFrame
        
        Returns:
            Text description of table content
        """
        description_parts = []
        
        # Table structure
        description_parts.append(
            f"Table with {len(df)} rows and {len(df.columns)} columns."
        )
        
        # Column names
        columns = ", ".join(df.columns.tolist())
        description_parts.append(f"Columns: {columns}.")
        
        # Sample values from first few rows
        if not df.empty:
            first_row = df.iloc[0].to_dict()
            sample = ", ".join([f"{k}: {v}" for k, v in first_row.items() if v])
            description_parts.append(f"Sample data: {sample}.")
        
        # Identify numeric columns and provide statistics
        try:
            numeric_cols = df.select_dtypes(include=["int", "float"]).columns
            if len(numeric_cols) > 0:
                description_parts.append(
                    f"Contains numeric data in columns: {', '.join(numeric_cols)}."
                )
        except Exception:
            pass
        
        return " ".join(description_parts)
