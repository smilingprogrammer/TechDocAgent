# TechDocAgent

<div align="center">

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-brightgreen)
![License](https://img.shields.io/badge/license-MIT-blue)
![Version](https://img.shields.io/badge/version-2.0.0-orange)

**AI-powered technical documentation generation for codebases**

[Features](#-features) • [Installation](#-installation) • [Quick Start](#-quick-start) • [Documentation](#-documentation-types-supported) • [Examples](#-examples)

</div>

---

## Overview

TechDocAgent is an intelligent documentation generation system that automatically creates comprehensive technical documentation from your codebase. Powered by Google's Gemini AI and advanced code analysis techniques, it transforms source code into human-readable documentation with minimal effort.

The project offers **two implementations**:

- **Basic (`techdocagent`)**: Lightweight, straightforward documentation generation for simple projects
- **Advanced (`techdocagent_advanced`)**: Enterprise-grade system with memory, semantic search, incremental updates, and feedback learning

---

## Features

| Feature | Description |
|---------|-------------|
| **🔍 Vector Search** | FAISS-powered semantic code search using embeddings |
| **Language Detection** | Automatic detection of 15+ programming languages |
| **Change Detection** | Git and hash-based change tracking with dependency analysis |
| **Incremental Updates** | Smart regeneration of only affected documentation |
| **Feedback Loop** | Rating system, corrections, and continuous improvement |
| **Multi-Format** | 9+ documentation types (README, API, Onboarding, etc.) |
| **AST Analysis** | Advanced Abstract Syntax Tree parsing for deep code understanding |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))

### Basic Installation

```bash
# Clone the repository
git clone https://github.com/smilingprogrammer/TechDocAgent.git
cd TechDocAgent

# Install dependencies
pip install -r requirements.txt

# Set your API key
export GEMINI_API_KEY="your-api-key-here"
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Install with CLI tools
pip install -e ".[cli]"

# Install everything
pip install -e ".[dev,cli]"
```

---

## Quick Start

### Basic Usage

```python
from techdocagent.ingestion import ingest_codebase
from techdocagent.analysis import analyze_file
from techdocagent.llm import generate_documentation

# Ingest your codebase
files = ingest_codebase('./your-project-path')

# Analyze files
metadata = [analyze_file(f) for f in files]

# Generate documentation
docs = generate_documentation(files, metadata)
print(docs)
```

### Advanced Usage

```python
from techdocagent_advanced import TechDocAgent

# Use context manager for automatic cleanup
with TechDocAgent() as agent:
    # Analyze codebase and build embeddings
    summary = agent.analyze_codebase()
    print(f"Analyzed {summary['total_files']} files")

    # Generate README
    readme = agent.generate_documentation('README')

    # Search code semantically
    results = agent.search_code("authentication logic")
    for chunk, score in results[:3]:
        print(f"  - {chunk['name']}: {score:.2f}")

    # Collect feedback for continuous improvement
    agent.collect_feedback(doc_id=1, rating=5, comment="Excellent!")
```

### Command Line (Advanced)

```bash
# Generate documentation
techdoc-advanced generate --type README --output docs/

# Update documentation after code changes
techdoc-advanced update --type README

# Search codebase
techdoc-advanced search "error handling"

# View statistics
techdoc-advanced stats
```

---

## Documentation Types Supported

| Type | Description |
|------|-------------|
| **README** | Comprehensive project documentation |
| **API** | API reference with endpoints and examples |
| **ONBOARDING** | Developer onboarding and setup guides |
| **CHANGELOG** | Automated changelog from git history |
| **ARCHITECTURE** | System architecture and design docs |
| **MODULE** | Per-module/file documentation |
| **FUNCTION** | Function-level detailed documentation |
| **TEST** | Test suite documentation |
| **DEPLOYMENT** | Deployment and operations guides |

### Configuration

Create a `.techdocagent.json` file in your project root:

```json
{
  "gemini_api_key": "your-api-key-here",
  "project_root": ".",
  "output_dir": "./docs",
  "features": {
    "embeddings": true,
    "change_detection": true,
    "feedback_loop": true,
    "ast_analysis": true
  },
  "temperature": 0.7,
  "max_tokens": 8000
}
```

Or use environment variables:

```bash
export GEMINI_API_KEY="your-api-key"
export TECHDOC_OUTPUT_DIR="./docs"
export TECHDOC_PROJECT_ROOT="."
```

---

## 💡 Examples

### Example 1: Generate Multiple Documentation Types

```python
from techdocagent_advanced import TechDocAgent

with TechDocAgent() as agent:
    # Analyze once
    agent.analyze_codebase()

    # Generate multiple doc types
    doc_types = ['README', 'API', 'ONBOARDING', 'ARCHITECTURE']
    for doc_type in doc_types:
        doc = agent.generate_documentation(doc_type)
        print(f"✅ {doc_type} generated ({len(doc)} chars)")
```

### Example 2: Incremental Updates

```python
from techdocagent_advanced import TechDocAgent

with TechDocAgent() as agent:
    # Initial documentation
    agent.analyze_codebase()
    agent.generate_documentation('README')

    # ... make code changes ...

    # Smart update - only regenerates if changed
    updated = agent.update_documentation('README')
    print("✅ Documentation updated!")
```

### Example 3: Semantic Code Search

```python
from techdocagent_advanced import TechDocAgent

with TechDocAgent() as agent:
    agent.analyze_codebase()

    # Natural language search
    queries = [
        "database connection logic",
        "error handling middleware",
        "user authentication"
    ]

    for query in queries:
        results = agent.search_code(query, top_k=3)
        print(f"\n🔍 Query: {query}")
        for chunk, score in results:
            print(f"  - {chunk['name']} (similarity: {score:.2f})")
```

You can find more examples [here](https://github.com/smilingprogrammer/TechDocAgent/blob/main/EXAMPLES.md)

## 🗺️ Roadmap

### Current Status

- ✅ Basic documentation generation
- ✅ Advanced memory system
- ✅ Vector embeddings and search
- ✅ Change detection
- ✅ Feedback loop
- ✅ Multi-format documentation

### Future Plans

- 🔜 CLI interface with rich output
- 🔜 Web UI for interactive documentation
- 🔜 GitHub Actions integration
- 🔜 Support for more output formats (HTML, PDF)
- 🔜 Plugin system for custom doc types
- 🔜 Multi-language documentation (i18n)
- 🔜 Custom LLM backend support (OpenAI, Claude, etc.)

---


<div align="center">

⭐ Star it GitHub — it motivates me a lot!

</div>
