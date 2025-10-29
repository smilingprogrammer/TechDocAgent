"""
change_detector.py
Change detection and incremental update system for TechDocAgent Advanced.

Provides:
- Detect changes in codebase using git diff or file hashes
- Identify affected code chunks and documentation
- Track dependencies between files
- Support incremental documentation updates
"""

import os
import subprocess
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime


class ChangeDetector:
    """
    Detects changes in codebase and identifies affected documentation.

    Features:
    - Git-based change detection
    - File hash comparison
    - Dependency tracking
    - Affected chunk identification
    """

    def __init__(self, root_path: str, memory_manager=None):
        """
        Initialize change detector.

        Args:
            root_path: Root path of the codebase
            memory_manager: Optional MemoryManager instance for hash comparison
        """
        self.root_path = Path(root_path)
        self.memory_manager = memory_manager
        self.is_git_repo = self._check_git_repo()

    def _check_git_repo(self) -> bool:
        """Check if the root path is a git repository."""
        git_dir = self.root_path / ".git"
        return git_dir.exists() and git_dir.is_dir()

    def get_changed_files_git(self, since_commit: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get changed files using git.

        Args:
            since_commit: Compare against this commit (default: HEAD)

        Returns:
            List of dictionaries with file_path and change_type
        """
        if not self.is_git_repo:
            return []

        try:
            # Get changed files
            if since_commit:
                cmd = ["git", "diff", "--name-status", since_commit]
            else:
                # Check uncommitted changes
                cmd = ["git", "status", "--porcelain"]

            result = subprocess.run(
                cmd,
                cwd=self.root_path,
                capture_output=True,
                text=True,
                check=True
            )

            changes = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue

                if since_commit:
                    # Format: M\tfile.py
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        status, file_path = parts[0], parts[1]
                        change_type = self._parse_git_status(status)
                        changes.append({
                            'file_path': str(self.root_path / file_path),
                            'change_type': change_type
                        })
                else:
                    # Format: M file.py or ?? file.py
                    parts = line.split(maxsplit=1)
                    if len(parts) >= 2:
                        status, file_path = parts[0], parts[1]
                        change_type = self._parse_git_status(status)
                        changes.append({
                            'file_path': str(self.root_path / file_path),
                            'change_type': change_type
                        })

            return changes

        except subprocess.CalledProcessError as e:
            print(f"Error running git command: {e}")
            return []

    def _parse_git_status(self, status: str) -> str:
        """
        Parse git status code to change type.

        Args:
            status: Git status code (M, A, D, ??, etc.)

        Returns:
            Change type ('modified', 'added', 'deleted')
        """
        status = status.strip()
        if status in ('M', 'MM', 'AM'):
            return 'modified'
        elif status in ('A', 'AA', '??'):
            return 'added'
        elif status in ('D', 'DD'):
            return 'deleted'
        elif status in ('R', 'RM'):
            return 'renamed'
        else:
            return 'modified'

    def get_changed_files_hash(self, file_paths: List[str]) -> List[Dict[str, str]]:
        """
        Detect changes by comparing file hashes with stored values.

        Args:
            file_paths: List of file paths to check

        Returns:
            List of dictionaries with file_path and change_type
        """
        if not self.memory_manager:
            return []

        changes = []

        # Check tracked files
        tracked_files = set(self.memory_manager.get_all_file_paths())

        for file_path in file_paths:
            if not os.path.exists(file_path):
                # File was deleted
                if file_path in tracked_files:
                    changes.append({
                        'file_path': file_path,
                        'change_type': 'deleted'
                    })
                continue

            # Read current content
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
            except Exception as e:
                print(f"Error reading {file_path}: {e}")
                continue

            # Check if changed
            if self.memory_manager.has_file_changed(file_path, content):
                if file_path in tracked_files:
                    change_type = 'modified'
                else:
                    change_type = 'added'

                changes.append({
                    'file_path': file_path,
                    'change_type': change_type
                })

        # Check for deleted files
        current_files = set(file_paths)
        for tracked_file in tracked_files:
            if tracked_file not in current_files:
                changes.append({
                    'file_path': tracked_file,
                    'change_type': 'deleted'
                })

        return changes

    def get_all_changes(self, file_paths: List[str], since_commit: Optional[str] = None) -> List[Dict[str, str]]:
        """
        Get all changes using both git and hash comparison.

        Args:
            file_paths: List of current file paths
            since_commit: Optional git commit to compare against

        Returns:
            List of change dictionaries
        """
        changes_map = {}

        # Try git first
        if self.is_git_repo:
            git_changes = self.get_changed_files_git(since_commit)
            for change in git_changes:
                changes_map[change['file_path']] = change

        # Fall back to hash comparison for any files not detected by git
        if self.memory_manager:
            hash_changes = self.get_changed_files_hash(file_paths)
            for change in hash_changes:
                if change['file_path'] not in changes_map:
                    changes_map[change['file_path']] = change

        return list(changes_map.values())

    def identify_affected_chunks(self, changed_files: List[Dict], all_chunks: List[Dict]) -> Set[str]:
        """
        Identify which code chunks are affected by file changes.

        Args:
            changed_files: List of changed file dictionaries
            all_chunks: List of all code chunks with file_path metadata

        Returns:
            Set of affected chunk identifiers
        """
        changed_paths = {change['file_path'] for change in changed_files}
        affected_chunks = set()

        for chunk in all_chunks:
            chunk_file = chunk.get('file_path', '')
            if chunk_file in changed_paths:
                # Create a unique identifier for the chunk
                chunk_id = f"{chunk_file}:{chunk.get('name', 'unknown')}:{chunk.get('start_line', 0)}"
                affected_chunks.add(chunk_id)

        return affected_chunks

    def find_dependencies(self, file_path: str, all_files: List[str]) -> List[str]:
        """
        Find files that depend on or are depended on by the given file.

        This is a simple implementation that looks for imports.
        Can be extended with more sophisticated dependency analysis.

        Args:
            file_path: File to analyze
            all_files: List of all files in codebase

        Returns:
            List of dependent file paths
        """
        dependencies = []

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
        except Exception:
            return dependencies

        # Extract potential imports/includes
        import_patterns = self._extract_imports(content, file_path)

        # Match imports to actual files
        for pattern in import_patterns:
            for other_file in all_files:
                if pattern in other_file or Path(other_file).stem == pattern:
                    dependencies.append(other_file)

        return dependencies

    def _extract_imports(self, content: str, file_path: str) -> List[str]:
        """
        Extract import statements from code.

        Args:
            content: File content
            file_path: File path (to determine language)

        Returns:
            List of imported module names
        """
        imports = []
        ext = Path(file_path).suffix.lower()

        lines = content.split('\n')

        if ext == '.py':
            # Python imports
            import re
            for line in lines:
                # from X import Y
                match = re.match(r'^\s*from\s+(\S+)\s+import', line)
                if match:
                    imports.append(match.group(1))
                # import X
                match = re.match(r'^\s*import\s+(\S+)', line)
                if match:
                    imports.append(match.group(1).split('.')[0])

        elif ext in ('.js', '.ts'):
            # JavaScript/TypeScript imports
            import re
            for line in lines:
                # import X from 'Y'
                match = re.search(r"from\s+['\"](.+?)['\"]", line)
                if match:
                    imports.append(match.group(1))
                # require('Y')
                match = re.search(r"require\(['\"](.+?)['\"]\)", line)
                if match:
                    imports.append(match.group(1))

        elif ext in ('.java', '.cpp', '.c', '.cs'):
            # Java, C++, C, C# imports
            import re
            for line in lines:
                # import/using/include statements
                match = re.search(r'^\s*(?:import|using|#include)\s+[<"]?(.+?)[>"]?;?$', line)
                if match:
                    imports.append(match.group(1))

        return imports

    def calculate_change_impact(self, changed_files: List[Dict], all_files: List[str]) -> Dict[str, Any]:
        """
        Calculate the impact of changes on the codebase.

        Args:
            changed_files: List of changed file dictionaries
            all_files: List of all files in codebase

        Returns:
            Dictionary with impact analysis
        """
        impact = {
            'direct_changes': len(changed_files),
            'affected_files': set(),
            'change_types': {},
            'high_impact_files': []
        }

        # Count change types
        for change in changed_files:
            change_type = change['change_type']
            impact['change_types'][change_type] = impact['change_types'].get(change_type, 0) + 1

        # Find affected files through dependencies
        for change in changed_files:
            file_path = change['file_path']
            impact['affected_files'].add(file_path)

            # Find dependencies
            deps = self.find_dependencies(file_path, all_files)
            impact['affected_files'].update(deps)

            # Mark high-impact files (those with many dependencies)
            if len(deps) > 5:
                impact['high_impact_files'].append({
                    'file': file_path,
                    'dependency_count': len(deps)
                })

        impact['total_affected_files'] = len(impact['affected_files'])
        impact['affected_files'] = list(impact['affected_files'])

        return impact

    def get_last_commit_hash(self) -> Optional[str]:
        """
        Get the last commit hash from git.

        Returns:
            Commit hash or None
        """
        if not self.is_git_repo:
            return None

        try:
            result = subprocess.run(
                ["git", "rev-parse", "HEAD"],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError:
            return None

    def get_file_history(self, file_path: str, limit: int = 10) -> List[Dict]:
        """
        Get commit history for a specific file.

        Args:
            file_path: Path to file
            limit: Maximum number of commits

        Returns:
            List of commit dictionaries
        """
        if not self.is_git_repo:
            return []

        try:
            result = subprocess.run(
                ["git", "log", "--pretty=format:%H|%an|%ae|%ad|%s", f"-{limit}", "--", file_path],
                cwd=self.root_path,
                capture_output=True,
                text=True,
                check=True
            )

            commits = []
            for line in result.stdout.strip().split('\n'):
                if not line:
                    continue
                parts = line.split('|')
                if len(parts) >= 5:
                    commits.append({
                        'hash': parts[0],
                        'author': parts[1],
                        'email': parts[2],
                        'date': parts[3],
                        'message': parts[4]
                    })

            return commits

        except subprocess.CalledProcessError:
            return []

    def should_update_documentation(self, doc_type: str, changed_files: List[Dict]) -> bool:
        """
        Determine if documentation should be updated based on changes.

        Args:
            doc_type: Type of documentation
            changed_files: List of changed files

        Returns:
            True if documentation should be updated
        """
        if not changed_files:
            return False

        # Always update for code changes
        code_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.go', '.rs'}

        for change in changed_files:
            ext = Path(change['file_path']).suffix.lower()
            if ext in code_extensions:
                return True

        # Update README if project structure changed
        if doc_type == 'README':
            for change in changed_files:
                file_name = Path(change['file_path']).name.lower()
                if file_name in ('setup.py', 'package.json', 'cargo.toml', 'pom.xml'):
                    return True

        return False
