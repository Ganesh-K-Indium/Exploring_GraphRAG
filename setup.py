"""
Setup script for the Graph RAG package.
"""
from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text() if readme_file.exists() else ""

setup(
    name="multimodal-graph-rag",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="Multimodal Graph RAG system for 10-K financial reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/multimodal-graph-rag",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Office/Business :: Financial",
    ],
    python_requires=">=3.10",
    install_requires=[
        "pypdf>=3.17.0",
        "pdfplumber>=0.10.0",
        "PyMuPDF>=1.23.0",
        "pillow>=10.0.0",
        "spacy>=3.7.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "neo4j>=5.14.0",
        "qdrant-client>=1.7.0",
        "voyageai>=0.2.0",
        "openai>=1.0.0",
        "transformers>=4.36.0",
        "torch>=2.1.0",
        "sentence-transformers>=2.2.2",
        "anthropic>=0.18.0",
        "fastapi>=0.109.0",
        "uvicorn>=0.27.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "python-dotenv>=1.0.0",
        "tqdm>=4.66.0",
        "loguru>=0.7.0",
        "aiohttp>=3.9.0",
        "pyyaml>=6.0.1",
        "python-multipart>=0.0.6",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.25.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "graph-rag-server=src.api.server:main",
        ],
    },
)
