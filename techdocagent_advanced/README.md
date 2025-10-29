# TechDocAgent Advanced

Next-generation technical documentation agent with memory, embeddings, and incremental updates.

## Overview

TechDocAgent Advanced is an intelligent documentation generation system that implements all the features from the [TechDocAgent_AdvancedRoadmap.md](../TechDocAgent_AdvancedRoadmap.md):

### Key Features

#### 1. Memory & Contextual Awareness
- **Persistent Storage**: SQLite-based memory system tracks codebase state, documentation history, and user feedback
- **Change Tracking**: File hash-based change detection identifies modifications
- **Session Context**: Maintains context across multiple documentation generation sessions
- **User Feedback Memory**: Stores corrections and preferences to improve future generations

#### 2. Multi-Doc & Multi-Format Support
- **README**: Comprehensive project documentation
- **API Documentation**: Detailed API reference docs
- **Onboarding Guides**: Step-by-step guides for new developers
- **Changelog**: Automated changelog generation from code changes
- **Architecture Docs**: System architecture documentation
- **Module/Function Docs**: Per-component documentation

#### 3. Embeddings & Semantic Search
- **Vector Embeddings**: Uses Gemini embeddings to represent code chunks
- **FAISS Integration**: Fast similarity search across the codebase
- **Semantic Retrieval**: Find relevant code using natural language queries
- **Context-Aware Generation**: Uses most relevant code for each doc type

#### 4. Change Detection & Incremental Updates
- **Git Integration**: Detects changes using git diff
- **File Hash Comparison**: Fallback change detection using content hashes
- **Dependency Tracking**: Identifies affected files and documentation
- **Selective Updates**: Only regenerates affected documentation sections

#### 5. Advanced Code Understanding
- **AST Analysis**: Deep code structure extraction (with Tree-sitter support)
- **Multi-Language Support**: Python, JavaScript, TypeScript, Java, C++, Go, Rust, and more
- **Relationship Detection**: Identifies inheritance, imports, and dependencies
- **Semantic Chunking**: Intelligent code splitting at function/class boundaries

#### 6. Feedback Loop System
- **Rating System**: Rate documentation quality (1-5 stars)
- **Corrections**: Submit corrections to improve future generations
- **Comments**: Add feedback and suggestions
- **Analytics**: Track feedback trends and common issues
- **Auto-Improvement**: Apply learned corrections to future prompts

#### 7. Configuration & Customization
- **JSON/YAML Config**: Flexible configuration files
- **Environment Variables**: Support for env-based configuration
- **Custom Templates**: Define your own documentation templates
- **Feature Toggles**: Enable/disable features as needed
- **Extensible**: Easy to add new doc types and languages

## Installation

### Basic Installation

```bash
# Install from requirements file
pip install -r requirements_advanced.txt

# Or install with setup.py
pip install -e .
```

### Optional Dependencies

```bash
# For CLI tools with rich output
pip install click rich tqdm

# For Tree-sitter AST parsing (requires compilation)
pip install tree-sitter

# For GPU-accelerated vector search
pip install faiss-gpu  # Instead of faiss-cpu
```

## Quick Start

### 1. Configuration

Create a `.techdocagent.json` file in your project root:

```json
{
  "gemini_api_key": "your-api-key-here",
  "project_root": ".",
  "output_dir": "./docs",
  "code_extensions": [".py", ".js", ".ts", ".java"],
  "features": {
    "embeddings": true,
    "change_detection": true,
    "feedback_loop": true,
    "ast_analysis": true
  }
}
```

Or use environment variables:

```bash
export GEMINI_API_KEY="your-api-key-here"
export TECHDOC_PROJECT_ROOT="."
export TECHDOC_OUTPUT_DIR="./docs"
```

### 2. Basic Usage

```python
from techdocagent_advanced import TechDocAgent

# Initialize agent
agent = TechDocAgent(config_path=".techdocagent.json")

# Analyze codebase and build embeddings
agent.analyze_codebase()

# Generate README
readme = agent.generate_documentation('README')
print(readme)

# Generate API documentation
api_docs = agent.generate_documentation('API')

# Update documentation after code changes
updated_readme = agent.update_documentation('README')

# Search codebase semantically
results = agent.search_code("authentication logic")
for chunk, score in results:
    print(f"{chunk['name']} (score: {score:.2f})")

# Get agent statistics
stats = agent.get_stats()
print(stats)

# Clean up
agent.close()
```

### 3. Using Context Manager

```python
from techdocagent_advanced import TechDocAgent

with TechDocAgent() as agent:
    # Analyze codebase
    summary = agent.analyze_codebase()
    print(f"Analyzed {summary['total_files']} files")

    # Generate multiple doc types
    for doc_type in ['README', 'API', 'ONBOARDING']:
        agent.generate_documentation(doc_type)

    # Collect feedback
    agent.collect_feedback(
        doc_id=1,
        rating=5,
        comment="Great documentation!"
    )
```

## Architecture

### Component Overview

```
techdocagent_advanced/
├── __init__.py           # Package initialization
├── agent.py              # Main orchestrator
├── memory.py             # Persistent storage and memory
├── embeddings.py         # Vector embeddings and search
├── change_detector.py    # Change detection system
├── feedback.py           # User feedback loop
├── doc_templates.py      # Documentation templates
├── ast_analyzer.py       # AST-based code analysis
└── config.py             # Configuration management
```

### Data Flow

1. **Ingestion**: Code files are scanned and filtered
2. **Analysis**: AST parsing extracts code structure
3. **Chunking**: Code is split into semantic chunks
4. **Embedding**: Chunks are embedded using Gemini
5. **Storage**: Embeddings and metadata stored in FAISS + SQLite
6. **Generation**: LLM generates docs using relevant context
7. **Feedback**: Users provide feedback for continuous improvement

### Memory System

The memory system uses SQLite to store:
- File metadata and content hashes
- Generated documentation history
- User feedback and corrections
- Analysis sessions
- Detected changes

### Embedding System

- Uses Gemini's `models/embedding-001`
- Stores embeddings in FAISS index
- Enables semantic search across codebase
- Automatically updates when code changes

## Advanced Features

### Change Detection

```python
from techdocagent_advanced import ChangeDetector, MemoryManager

memory = MemoryManager()
detector = ChangeDetector("./my-project", memory)

# Get changed files
changes = detector.get_changed_files_git(since_commit="HEAD~5")

# Calculate impact
impact = detector.calculate_change_impact(changes, all_files)
print(f"Changes affect {impact['total_affected_files']} files")

# Check if docs need update
should_update = detector.should_update_documentation('README', changes)
```

### Semantic Code Search

```python
from techdocagent_advanced import EmbeddingManager

embeddings = EmbeddingManager(api_key="your-key")

# Search for code
results = embeddings.search("user authentication", top_k=5)

for chunk, similarity in results:
    print(f"{chunk['name']} in {chunk['file_path']}")
    print(f"Similarity: {similarity:.2f}")
    print(f"Code preview: {chunk['code'][:100]}...")
```

### Feedback Analysis

```python
from techdocagent_advanced import FeedbackManager, MemoryManager

memory = MemoryManager()
feedback = FeedbackManager(memory)

# Get feedback report
report = feedback.create_feedback_report('README')
print(report)

# Get improvement suggestions
suggestions = feedback.get_improvement_suggestions()
for suggestion in suggestions:
    print(f"- {suggestion}")
```

### Custom Templates

```python
from techdocagent_advanced import DocTemplates

# Define custom template
custom_template = """
Generate API documentation with these sections:
{custom_sections}

Code to document:
{code_content}
"""

# Use with agent
context = {
    'custom_sections': 'Overview, Endpoints, Examples',
    'code_content': 'your code here'
}

filled = DocTemplates.fill_template(custom_template, context)
```

## Configuration Options

### Core Settings

- `gemini_api_key`: Your Gemini API key
- `project_root`: Root directory of your project
- `output_dir`: Where to save generated docs
- `memory_db_path`: SQLite database path
- `embeddings_path`: FAISS index directory

### Feature Toggles

```json
{
  "features": {
    "embeddings": true,
    "change_detection": true,
    "feedback_loop": true,
    "ast_analysis": true,
    "versioning": true
  }
}
```

### Analysis Settings

- `code_extensions`: File extensions to analyze
- `ignore_patterns`: Patterns to ignore
- `respect_gitignore`: Honor .gitignore rules
- `use_ast_analysis`: Use AST parsing
- `max_chunk_size`: Maximum lines per chunk

### LLM Settings

- `temperature`: Generation temperature (0.0-1.0)
- `max_tokens`: Maximum output tokens
- `top_p`: Nucleus sampling parameter
- `top_k`: Top-k sampling parameter

## Documentation Types

### Available Templates

- `README`: Comprehensive project README
- `API`: API reference documentation
- `ONBOARDING`: Developer onboarding guide
- `CHANGELOG`: Automated changelog
- `ARCHITECTURE`: System architecture docs
- `MODULE`: Per-module documentation
- `FUNCTION`: Per-function documentation
- `TEST`: Test documentation
- `DEPLOYMENT`: Deployment guide

### Custom Doc Types

Extend `DocTemplates` to add your own:

```python
from techdocagent_advanced.doc_templates import DocTemplates

class MyTemplates(DocTemplates):
    @staticmethod
    def get_custom_template():
        return """
        Your custom template here with {placeholders}
        """

# Register
DocTemplates.get_custom_template = MyTemplates.get_custom_template
```

## Performance Considerations

### For Large Codebases

- Use `batch_size` to control memory usage
- Enable `parallel_processing` for faster analysis
- Consider using `faiss-gpu` for faster search
- Use incremental updates instead of full regeneration

### Optimization Tips

1. **Initial Analysis**: Run once, then use incremental updates
2. **Embeddings**: Persist embeddings to avoid regeneration
3. **Change Detection**: Use git integration for efficiency
4. **Chunk Size**: Balance between context and performance
5. **FAISS Index**: Use IVF indexes for very large codebases

## Troubleshooting

### Common Issues

**No Embeddings Generated**
- Check API key configuration
- Verify `features.embeddings` is enabled
- Check network connectivity

**Change Detection Not Working**
- Ensure project is a git repository
- Check `use_git_tracking` setting
- Verify file paths are correct

**Out of Memory**
- Reduce `batch_size`
- Decrease `max_chunk_size`
- Use `faiss-cpu` with smaller datasets

## Comparison with Basic TechDocAgent

| Feature | Basic | Advanced |
|---------|-------|----------|
| Memory System | ❌ | ✅ SQLite |
| Embeddings | ❌ | ✅ Gemini + FAISS |
| Change Detection | ❌ | ✅ Git + Hash |
| Incremental Updates | ❌ | ✅ |
| Feedback Loop | ❌ | ✅ |
| AST Analysis | Basic | ✅ Advanced |
| Multiple Doc Types | Limited | ✅ 9+ Types |
| Semantic Search | ❌ | ✅ |
| Configuration | Basic | ✅ Full |

## Roadmap

See [TechDocAgent_AdvancedRoadmap.md](../TechDocAgent_AdvancedRoadmap.md) for the complete roadmap.

### Upcoming Features

- CLI and Web UI
- GitHub Actions integration
- Multi-language doc generation
- Plugin system
- Tree-sitter full integration
- Custom LLM backends

## Contributing

Contributions are welcome! Areas for improvement:

- Add more documentation templates
- Improve AST analysis for more languages
- Enhance feedback analysis
- Add more output formats (HTML, PDF)
- Build CLI interface
- Create web UI

## License

MIT License - see LICENSE file for details

## Credits

Built with:
- Google Gemini for LLM and embeddings
- FAISS for vector search
- SQLite for persistent storage
- Tree-sitter for AST parsing (optional)
