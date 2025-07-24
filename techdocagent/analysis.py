"""
analysis.py
Module for code analysis: detects programming language and extracts code structure.
"""
import os
from pathlib import Path

# Mapping of file extensions to languages
EXTENSION_LANGUAGE_MAP = {
    '.py': 'Python',
    '.js': 'JavaScript',
    '.ts': 'TypeScript',
    '.java': 'Java',
    '.c': 'C',
    '.cpp': 'C++',
    '.cs': 'C#',
    '.go': 'Go',
    '.rb': 'Ruby',
    '.php': 'PHP',
    '.rs': 'Rust',
    '.swift': 'Swift',
    '.kt': 'Kotlin',
    '.m': 'Objective-C',
    '.scala': 'Scala',
    '.sh': 'Shell',
    '.pl': 'Perl',
    '.lua': 'Lua',
    '.dart': 'Dart',
    '.html': 'HTML',
    '.css': 'CSS',
    '.json': 'JSON',
    '.xml': 'XML',
    '.yml': 'YAML',
    '.yaml': 'YAML',
}

def detect_language(file_path):
    ext = Path(file_path).suffix.lower()
    return EXTENSION_LANGUAGE_MAP.get(ext, 'Unknown')

def analyze_file(file_path):
    """
    Detect the programming language and extract code structure from the given file.
    Returns language and structure metadata.
    """
    language = detect_language(file_path)
    file_stats = os.stat(file_path)
    metadata = {
        'file_path': str(file_path),
        'file_name': Path(file_path).name,
        'size_bytes': file_stats.st_size,
        'language': language,
    }
    return metadata
    