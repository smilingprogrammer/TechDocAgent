
## Advanced Features And It Examples (Will Still Add more Usage Examples)

### Memory System

The memory system uses SQLite to store:

- **File Metadata**: Hashes, languages, modification times
- **Documentation History**: All generated docs with versions
- **User Feedback**: Ratings, corrections, and comments
- **Change Tracking**: What changed and when
- **Session Data**: Analysis session information

```python
from techdocagent_advanced.memory import MemoryManager

memory = MemoryManager()

# Store file metadata
memory.store_file_metadata(file_path, content, language, metadata)

# Check if file changed
has_changed = memory.has_file_changed(file_path, current_content)

# Get documentation history
docs = memory.get_latest_documentation('README')
```

### Vector Search with Embeddings

Semantic code search powered by Gemini embeddings and FAISS:

```python
from techdocagent_advanced.embeddings import EmbeddingManager

embeddings = EmbeddingManager(api_key="your-key")

# Add code chunks
for chunk in chunks:
    embeddings.add_chunk(chunk, file_path, language)

# Search semantically
results = embeddings.search("authentication logic", top_k=5)

# Get statistics
stats = embeddings.get_stats()
```

### Change Detection

Intelligent change detection using Git and file hashes:

```python
from techdocagent_advanced.change_detector import ChangeDetector

detector = ChangeDetector(project_root, memory_manager)

# Get changes via Git
changes = detector.get_changed_files_git(since_commit="HEAD~5")

# Calculate impact
impact = detector.calculate_change_impact(changes, all_files)

# Determine if docs need update
should_update = detector.should_update_documentation('README', changes)
```

### Feedback Collection

```python
from techdocagent_advanced import TechDocAgent

with TechDocAgent() as agent:
    agent.analyze_codebase()
    agent.generate_documentation('README')

    # Collect user feedback
    agent.collect_feedback(
        doc_id=1,
        rating=4,
        comment="Good docs, but needs more examples"
    )

    # Submit corrections
    agent.collect_feedback(
        doc_id=1,
        correction="The installation section should mention Python 3.8+"
    )

    # View feedback report
    report = agent.get_feedback_report()
    print(report)
```