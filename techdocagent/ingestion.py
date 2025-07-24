"""
ingestion.py
Module for codebase ingestion: recursively scans directories, filters code files, and respects .gitignore rules.
"""

import os
from pathlib import Path
import pathspec

# Default set of code file extensions (can be expanded)
CODE_EXTENSIONS = {
    '.py', '.js', '.ts', '.java', '.c', '.cpp', '.cs', '.go', '.rb', '.php', '.rs', '.swift', '.kt', '.m', '.scala', '.sh', '.pl', '.lua', '.dart', '.html', '.css', '.json', '.xml', '.yml', '.yaml'
}

def load_gitignore(root_path):
    gitignore_path = Path(root_path) / '.gitignore'
    if gitignore_path.exists():
        with open(gitignore_path, 'r') as f:
            return pathspec.PathSpec.from_lines('gitwildmatch', f)
    return None

def ingest_codebase(root_path):
    """
    Recursively scan the root_path, filter code files by extension, and respect .gitignore.
    Returns a list of code file paths.
    """
    root = Path(root_path)
    spec = load_gitignore(root)
    code_files = []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        # Skip ignored directories
        if spec and rel_dir != '.' and spec.match_file(rel_dir + '/'):  # Add trailing slash for directories
            dirnames[:] = []  # Don't recurse into this directory
            continue
        for filename in filenames:
            file_path = Path(dirpath) / filename
            rel_file = os.path.relpath(file_path, root)
            if spec and spec.match_file(rel_file):
                continue
            if file_path.suffix.lower() in CODE_EXTENSIONS:
                code_files.append(str(file_path))
    return code_files 