"""
chunking.py
Module for code chunking: splits code into logical chunks (functions, classes, modules, etc.).
"""
import re

def chunk_code(file_content, language):
    """
    Split code into logical chunks based on language.
    Returns a list of code chunks with metadata.
    """
    chunks = []
    lines = file_content.splitlines()
    if language == 'Python':
        pattern = re.compile(r'^(def|class)\s+(\w+)\s*\(?.*\)?:', re.MULTILINE)
        matches = list(pattern.finditer(file_content))
        for i, match in enumerate(matches):
            chunk_type = match.group(1)
            name = match.group(2)
            start_line = file_content[:match.start()].count('\n') + 1
            if i + 1 < len(matches):
                end_line = file_content[:matches[i+1].start()].count('\n')
            else:
                end_line = len(lines)
            code = '\n'.join(lines[start_line-1:end_line])
            chunks.append({
                'type': chunk_type,
                'name': name,
                'start_line': start_line,
                'end_line': end_line,
                'code': code
            })
        if not matches:
            # No functions/classes found, treat whole file as one chunk
            chunks.append({
                'type': 'file',
                'name': None,
                'start_line': 1,
                'end_line': len(lines),
                'code': file_content
            })
    else:
        # For other languages, treat the whole file as a single chunk
        chunks.append({
            'type': 'file',
            'name': None,
            'start_line': 1,
            'end_line': len(lines),
            'code': file_content
        })
    return chunks 