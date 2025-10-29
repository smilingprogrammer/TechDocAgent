"""
Setup script for TechDocAgent Advanced
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read the README file
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="techdocagent-advanced",
    version="2.0.0",
    author="TechDocAgent Team",
    author_email="",
    description="Advanced technical documentation agent with memory, embeddings, and incremental updates",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/techdocagent",
    packages=find_packages(include=['techdocagent_advanced', 'techdocagent_advanced.*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Documentation",
        "Topic :: Software Development :: Code Generators",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "google-generativeai>=0.3.0",
        "pathspec>=0.11.0",
        "faiss-cpu>=1.7.4",
        "numpy>=1.24.0",
        "PyYAML>=6.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.4.0",
        ],
        "cli": [
            "click>=8.1.0",
            "rich>=13.0.0",
            "tqdm>=4.65.0",
        ],
        "ast": [
            # "tree-sitter>=0.20.0",  # Uncomment if you want to use tree-sitter
        ],
    },
    entry_points={
        "console_scripts": [
            "techdoc-advanced=techdocagent_advanced.cli:main",
        ],
    },
    include_package_data=True,
    keywords="documentation code-generation llm gemini technical-docs",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/techdocagent/issues",
        "Source": "https://github.com/yourusername/techdocagent",
        "Documentation": "https://github.com/yourusername/techdocagent/blob/main/README.md",
    },
)
