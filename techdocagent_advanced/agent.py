"""
agent.py
Main TechDocAgent Advanced orchestrator.

Coordinates all components to provide advanced documentation generation with:
- Memory and contextual awareness
- Embeddings and semantic search
- Change detection and incremental updates
- Multi-format documentation
- Feedback loop
"""

import os
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

# Import from existing techdocagent (basic functionality)
import sys
sys.path.append(str(Path(__file__).parent.parent))

try:
    from techdocagent.ingestion import ingest_codebase
    from techdocagent.analysis import detect_language, analyze_file
    from techdocagent.llm import generate_documentation as basic_generate
except ImportError:
    print("Warning: Could not import from techdocagent. Some basic features may not work.")
    ingest_codebase = None
    detect_language = None
    analyze_file = None
    basic_generate = None

# Import advanced components
from .memory import MemoryManager
from .embeddings import EmbeddingManager
from .change_detector import ChangeDetector
from .feedback import FeedbackManager
from .doc_templates import DocTemplates
from .ast_analyzer import ASTAnalyzer
from .config import AgentConfig, ConfigManager

import google.generativeai as genai


class TechDocAgent:
    """
    Advanced Technical Documentation Agent.

    Orchestrates all components to provide intelligent, context-aware
    documentation generation with memory, embeddings, and incremental updates.
    """

    def __init__(self, config: Optional[AgentConfig] = None, config_path: Optional[str] = None):
        """
        Initialize TechDocAgent Advanced.

        Args:
            config: AgentConfig instance (optional)
            config_path: Path to config file (optional)
        """
        # Load configuration
        if config:
            self.config = config
        else:
            config_manager = ConfigManager(config_path)
            self.config = config_manager.config

        # Validate config
        errors = self.config.validate()
        if errors:
            print("Warning: Configuration has errors:")
            for error in errors:
                print(f"  - {error}")

        # Initialize API
        if self.config.gemini_api_key:
            genai.configure(api_key=self.config.gemini_api_key)

        # Initialize components
        self.memory = MemoryManager(self.config.memory_db_path)
        self.embeddings = EmbeddingManager(
            api_key=self.config.gemini_api_key,
            index_path=self.config.embeddings_path
        ) if self.config.features.get('embeddings', True) else None

        self.change_detector = ChangeDetector(
            self.config.project_root,
            self.memory
        ) if self.config.features.get('change_detection', True) else None

        self.feedback = FeedbackManager(self.memory) if self.config.features.get('feedback_loop', True) else None

        self.ast_analyzer = ASTAnalyzer() if self.config.features.get('ast_analysis', True) else None

        # Session management
        self.session_id = str(uuid.uuid4())
        self.memory.create_session(self.session_id, {'started_at': str(datetime.now())})

        print(f"TechDocAgent Advanced initialized (Session: {self.session_id[:8]})")

    def analyze_codebase(self, root_path: Optional[str] = None, force_reanalyze: bool = False) -> Dict[str, Any]:
        """
        Analyze entire codebase and build embeddings.

        Args:
            root_path: Root directory to analyze (uses config default if None)
            force_reanalyze: Force re-analysis even if no changes detected

        Returns:
            Analysis summary
        """
        root_path = root_path or self.config.project_root
        print(f"\nAnalyzing codebase: {root_path}")

        # Ingest codebase
        if ingest_codebase:
            code_files = ingest_codebase(root_path)
        else:
            # Fallback ingestion
            code_files = self._fallback_ingest(root_path)

        print(f"Found {len(code_files)} code files")

        # Detect changes
        changes = []
        if self.change_detector and not force_reanalyze:
            changes = self.change_detector.get_all_changes(code_files)
            if changes:
                print(f"Detected {len(changes)} changed files")
            else:
                print("No changes detected since last analysis")

        # Analyze files
        analyzed_count = 0
        new_chunks_count = 0

        for file_path in code_files:
            # Skip if no changes and not forcing
            if not force_reanalyze and changes:
                if not any(c['file_path'] == file_path for c in changes):
                    continue

            try:
                # Read file
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()

                # Detect language
                language = detect_language(file_path) if detect_language else self._fallback_detect_language(file_path)

                # Analyze with AST if available
                if self.ast_analyzer:
                    chunks = self.ast_analyzer.extract_chunks(file_path, content, language)
                else:
                    # Fallback chunking
                    chunks = self._fallback_chunk(content, language)

                # Store in memory
                metadata = analyze_file(file_path) if analyze_file else {}
                self.memory.store_file_metadata(file_path, content, language, metadata)

                # Generate embeddings
                if self.embeddings:
                    for chunk in chunks:
                        self.embeddings.add_chunk(chunk, file_path, language)
                        new_chunks_count += 1

                analyzed_count += 1

                if analyzed_count % 10 == 0:
                    print(f"  Analyzed {analyzed_count} files...")

            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")

        # Save embeddings
        if self.embeddings:
            self.embeddings.save()

        summary = {
            'total_files': len(code_files),
            'analyzed_files': analyzed_count,
            'new_chunks': new_chunks_count,
            'changes_detected': len(changes),
            'session_id': self.session_id
        }

        print(f"\nAnalysis complete:")
        print(f"  - Total files: {summary['total_files']}")
        print(f"  - Analyzed: {summary['analyzed_files']}")
        print(f"  - New chunks: {summary['new_chunks']}")
        print(f"  - Changes: {summary['changes_detected']}")

        return summary

    def generate_documentation(self, doc_type: str = 'README', output_path: Optional[str] = None,
                             custom_context: Optional[Dict] = None) -> str:
        """
        Generate documentation of specified type.

        Args:
            doc_type: Type of documentation to generate
            output_path: Where to save the documentation
            custom_context: Additional context for generation

        Returns:
            Generated documentation content
        """
        print(f"\nGenerating {doc_type} documentation...")

        # Get template
        template = DocTemplates.get_template(doc_type)
        if not template:
            raise ValueError(f"Unknown documentation type: {doc_type}")

        # Gather context
        context = self._gather_context(doc_type, custom_context)

        # Apply feedback improvements if available
        if self.feedback:
            template = self.feedback.apply_corrections_to_prompt(doc_type, template)

        # Fill template
        filled_prompt = DocTemplates.fill_template(template, context)

        # Generate with LLM
        print("  Calling LLM...")
        documentation = self._call_llm(filled_prompt)

        # Post-process
        documentation = self._post_process_documentation(documentation, doc_type)

        # Store in memory
        version_hash = self.change_detector.get_last_commit_hash() if self.change_detector else None
        doc_id = self.memory.store_documentation(
            doc_type=doc_type,
            content=documentation,
            version_hash=version_hash,
            metadata=context
        )

        print(f"  Documentation generated (ID: {doc_id})")

        # Save to file
        if output_path or self.config.auto_save:
            save_path = output_path or self._get_default_output_path(doc_type)
            self._save_documentation(documentation, save_path)
            print(f"  Saved to: {save_path}")

        return documentation

    def update_documentation(self, doc_type: str = 'README', output_path: Optional[str] = None) -> str:
        """
        Update existing documentation based on recent changes.

        Args:
            doc_type: Type of documentation to update
            output_path: Where to save the updated documentation

        Returns:
            Updated documentation content
        """
        print(f"\nUpdating {doc_type} documentation...")

        # Check for changes
        if not self.change_detector:
            print("Change detection not available. Generating new documentation.")
            return self.generate_documentation(doc_type, output_path)

        code_files = ingest_codebase(self.config.project_root) if ingest_codebase else []
        changes = self.change_detector.get_all_changes(code_files)

        if not changes:
            print("No changes detected. Documentation is up to date.")
            latest_doc = self.memory.get_latest_documentation(doc_type)
            return latest_doc['content'] if latest_doc else ""

        print(f"  Found {len(changes)} changed files")

        # Check if update is needed
        if not self.change_detector.should_update_documentation(doc_type, changes):
            print("  Changes don't require documentation update")
            latest_doc = self.memory.get_latest_documentation(doc_type)
            return latest_doc['content'] if latest_doc else ""

        # Get existing documentation
        existing_doc = self.memory.get_latest_documentation(doc_type)

        # Generate updated documentation with change context
        context = self._gather_context(doc_type, {'changes': changes, 'existing_doc': existing_doc})

        # Use update-specific template
        template = self._get_update_template(doc_type)
        filled_prompt = DocTemplates.fill_template(template, context)

        # Generate with LLM
        print("  Generating update...")
        updated_doc = self._call_llm(filled_prompt)

        # Post-process
        updated_doc = self._post_process_documentation(updated_doc, doc_type)

        # Store
        version_hash = self.change_detector.get_last_commit_hash()
        doc_id = self.memory.store_documentation(
            doc_type=doc_type,
            content=updated_doc,
            version_hash=version_hash,
            metadata={'update': True, 'changes': len(changes)}
        )

        print(f"  Documentation updated (ID: {doc_id})")

        # Save
        if output_path or self.config.auto_save:
            save_path = output_path or self._get_default_output_path(doc_type)
            self._save_documentation(updated_doc, save_path)
            print(f"  Saved to: {save_path}")

        return updated_doc

    def search_code(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Search codebase using semantic search.

        Args:
            query: Search query
            top_k: Number of results to return

        Returns:
            List of (chunk_metadata, similarity_score) tuples
        """
        if not self.embeddings:
            print("Embeddings not available")
            return []

        return self.embeddings.search(query, top_k)

    def collect_feedback(self, doc_id: int, rating: Optional[int] = None,
                        correction: Optional[str] = None, comment: Optional[str] = None):
        """
        Collect feedback for generated documentation.

        Args:
            doc_id: Documentation ID
            rating: Rating 1-5
            correction: Corrected text
            comment: User comment
        """
        if not self.feedback:
            print("Feedback system not available")
            return

        if rating:
            self.feedback.collect_rating(doc_id, rating, comment)

        if correction:
            self.feedback.collect_correction(doc_id, correction, comment)

        if comment and not rating and not correction:
            self.feedback.collect_comment(doc_id, comment)

        print("Feedback collected successfully")

    def get_feedback_report(self, doc_type: Optional[str] = None) -> str:
        """
        Generate feedback report.

        Args:
            doc_type: Optional filter by doc type

        Returns:
            Formatted report
        """
        if not self.feedback:
            return "Feedback system not available"

        return self.feedback.create_feedback_report(doc_type)

    def get_stats(self) -> Dict[str, Any]:
        """Get agent statistics."""
        stats = {
            'session_id': self.session_id,
            'project_root': self.config.project_root,
            'files_tracked': len(self.memory.get_all_file_paths()),
        }

        if self.embeddings:
            stats['embeddings'] = self.embeddings.get_stats()

        if self.feedback:
            stats['feedback'] = self.feedback.analyze_feedback()

        return stats

    def _gather_context(self, doc_type: str, custom_context: Optional[Dict] = None) -> Dict[str, Any]:
        """Gather context for documentation generation."""
        context = custom_context or {}

        # Basic project info
        context['project_root'] = self.config.project_root
        context['project_name'] = Path(self.config.project_root).name

        # Get relevant code using embeddings
        if self.embeddings and len(self.embeddings) > 0:
            query = f"main functionality for {doc_type} documentation"
            relevant_chunks = self.embeddings.search(query, top_k=10)

            context['key_components'] = self._format_chunks(relevant_chunks[:5])
            context['sample_code'] = self._format_code_samples(relevant_chunks[:3])

        # Codebase structure
        context['codebase_structure'] = self._get_structure_summary()

        # Language statistics
        context['primary_language'] = self._get_primary_language()

        # File counts
        context['file_count'] = len(self.memory.get_all_file_paths())

        # Fill in any missing required fields with defaults
        context.setdefault('total_lines', 'Unknown')
        context.setdefault('tech_stack', 'To be determined')
        context.setdefault('complexity_level', 'Medium')
        context.setdefault('codebase_overview', 'See structure and components')
        context.setdefault('setup_info', 'See installation section')

        return context

    def _call_llm(self, prompt: str) -> str:
        """Call LLM to generate documentation."""
        try:
            model = genai.GenerativeModel(self.config.generation_model)

            response = model.generate_content(
                prompt,
                generation_config={
                    'temperature': self.config.temperature,
                    'max_output_tokens': self.config.max_tokens,
                    'top_p': self.config.top_p,
                    'top_k': self.config.top_k,
                }
            )

            return response.text

        except Exception as e:
            print(f"Error calling LLM: {e}")
            return f"Error generating documentation: {e}"

    def _post_process_documentation(self, content: str, doc_type: str) -> str:
        """Post-process generated documentation."""
        # Remove any potential API keys or secrets (basic check)
        import re

        # Remove common secret patterns
        patterns = [
            r'sk-[a-zA-Z0-9]{48}',  # OpenAI-style keys
            r'AIza[a-zA-Z0-9_-]{35}',  # Google API keys
            r'[a-zA-Z0-9]{32,}',  # Long hex strings (potential keys)
        ]

        for pattern in patterns:
            if re.search(pattern, content):
                print(f"Warning: Potential secret detected in documentation")

        return content.strip()

    def _save_documentation(self, content: str, path: str):
        """Save documentation to file."""
        output_path = Path(path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(content)

    def _get_default_output_path(self, doc_type: str) -> str:
        """Get default output path for documentation type."""
        output_dir = Path(self.config.output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        filename_map = {
            'README': 'README.md',
            'API': 'API.md',
            'ONBOARDING': 'ONBOARDING.md',
            'CHANGELOG': 'CHANGELOG.md',
            'ARCHITECTURE': 'ARCHITECTURE.md',
        }

        filename = filename_map.get(doc_type, f'{doc_type}.md')
        return str(output_dir / filename)

    def _get_update_template(self, doc_type: str) -> str:
        """Get template for updating documentation."""
        base_template = DocTemplates.get_template(doc_type)

        update_addendum = """

# Update Context
The codebase has changed. Here are the changes:
{changes}

Previous documentation:
{existing_doc}

Please update the documentation to reflect these changes while preserving the overall structure and style.
"""

        return base_template + update_addendum

    def _format_chunks(self, chunks: List[Tuple[Dict, float]]) -> str:
        """Format code chunks for context."""
        if not chunks:
            return "No relevant code chunks found"

        formatted = []
        for chunk, score in chunks:
            formatted.append(f"- {chunk['name']} ({chunk['chunk_type']}) in {Path(chunk['file_path']).name}")

        return "\n".join(formatted)

    def _format_code_samples(self, chunks: List[Tuple[Dict, float]]) -> str:
        """Format code samples for context."""
        if not chunks:
            return "No code samples available"

        formatted = []
        for chunk, score in chunks[:2]:  # Limit to 2 samples
            code = chunk.get('code', chunk.get('full_code', ''))[:300]
            formatted.append(f"```{chunk.get('language', '').lower()}\n{code}\n```")

        return "\n\n".join(formatted)

    def _get_structure_summary(self) -> str:
        """Get codebase structure summary."""
        # Placeholder - would analyze directory structure
        return "Project structure includes main source files and configuration"

    def _get_primary_language(self) -> str:
        """Get primary programming language."""
        # Simple heuristic - count files by language
        if self.embeddings and hasattr(self.embeddings, 'chunks'):
            langs = {}
            for chunk in self.embeddings.chunks:
                lang = chunk.get('language', 'Unknown')
                langs[lang] = langs.get(lang, 0) + 1

            if langs:
                return max(langs, key=langs.get)

        return "Unknown"

    def _fallback_ingest(self, root_path: str) -> List[str]:
        """Fallback file ingestion."""
        code_files = []
        for ext in self.config.code_extensions:
            code_files.extend(Path(root_path).rglob(f'*{ext}'))
        return [str(f) for f in code_files]

    def _fallback_detect_language(self, file_path: str) -> str:
        """Fallback language detection."""
        ext_map = {'.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript'}
        ext = Path(file_path).suffix
        return ext_map.get(ext, 'Unknown')

    def _fallback_chunk(self, content: str, language: str) -> List[Dict]:
        """Fallback chunking."""
        return [{
            'type': 'file',
            'name': 'full_file',
            'start_line': 1,
            'end_line': len(content.split('\n')),
            'code': content[:1000]  # First 1000 chars
        }]

    def close(self):
        """Clean up resources."""
        self.memory.close_session(self.session_id)
        self.memory.close()
        print(f"Session {self.session_id[:8]} closed")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
