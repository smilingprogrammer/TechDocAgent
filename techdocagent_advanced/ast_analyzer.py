"""
ast_analyzer.py
Advanced AST-based code analysis using Tree-sitter for TechDocAgent Advanced.

Provides:
- Multi-language AST parsing with Tree-sitter
- Deep code structure extraction
- Symbol extraction (classes, functions, variables)
- Relationship detection (inheritance, imports, calls)
- Enhanced chunking with semantic boundaries
"""

import os
from pathlib import Path
from typing import Dict, List, Optional, Any, Set, Tuple

# Tree-sitter is optional - fallback to regex if not available
try:
    from tree_sitter import Language, Parser
    TREE_SITTER_AVAILABLE = True
except ImportError:
    TREE_SITTER_AVAILABLE = False
    print("Warning: tree-sitter not installed. Using fallback analysis.")


class ASTAnalyzer:
    """
    Advanced code analyzer using AST parsing.

    Features:
    - Multi-language AST parsing
    - Extract classes, functions, methods
    - Identify relationships and dependencies
    - Enhanced code chunking
    """

    def __init__(self, languages_path: Optional[str] = None):
        """
        Initialize AST analyzer.

        Args:
            languages_path: Path to tree-sitter language binaries (optional)
        """
        self.languages_path = languages_path
        self.parsers = {}

        if TREE_SITTER_AVAILABLE and languages_path:
            self._load_languages()

    def _load_languages(self):
        """Load tree-sitter language parsers."""
        # This would load pre-compiled tree-sitter language binaries
        # For now, it's a placeholder
        supported_languages = ['python', 'javascript', 'typescript', 'java', 'cpp', 'go', 'rust']

        for lang in supported_languages:
            try:
                # In a real implementation, you would load the compiled language library
                # language = Language(self.languages_path, lang)
                # parser = Parser()
                # parser.set_language(language)
                # self.parsers[lang] = parser
                pass
            except Exception as e:
                print(f"Could not load {lang} parser: {e}")

    def analyze_file(self, file_path: str, content: str, language: str) -> Dict[str, Any]:
        """
        Analyze a code file using AST parsing.

        Args:
            file_path: Path to the file
            content: File content
            language: Programming language

        Returns:
            Analysis results with structure, symbols, and relationships
        """
        lang_lower = language.lower()

        # Use tree-sitter if available, otherwise fallback
        if TREE_SITTER_AVAILABLE and lang_lower in self.parsers:
            return self._analyze_with_treesitter(file_path, content, lang_lower)
        else:
            return self._analyze_with_fallback(file_path, content, language)

    def _analyze_with_treesitter(self, file_path: str, content: str, language: str) -> Dict[str, Any]:
        """
        Analyze code using tree-sitter.

        Args:
            file_path: File path
            content: Code content
            language: Language name

        Returns:
            Analysis results
        """
        # Placeholder for tree-sitter implementation
        # In a full implementation, this would use tree-sitter queries
        parser = self.parsers.get(language)

        if not parser:
            return self._analyze_with_fallback(file_path, content, language)

        # Parse the code
        tree = parser.parse(bytes(content, 'utf-8'))
        root_node = tree.root_node

        # Extract information from AST
        result = {
            'file_path': file_path,
            'language': language,
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'relationships': []
        }

        # This would include AST traversal logic
        # For different node types in different languages

        return result

    def _analyze_with_fallback(self, file_path: str, content: str, language: str) -> Dict[str, Any]:
        """
        Fallback analysis using regex patterns.

        Args:
            file_path: File path
            content: Code content
            language: Language name

        Returns:
            Analysis results
        """
        result = {
            'file_path': file_path,
            'language': language,
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'relationships': []
        }

        if language == 'Python':
            result = self._analyze_python(content)
        elif language in ('JavaScript', 'TypeScript'):
            result = self._analyze_javascript(content)
        elif language == 'Java':
            result = self._analyze_java(content)
        elif language in ('C++', 'C'):
            result = self._analyze_cpp(content)
        elif language == 'Go':
            result = self._analyze_go(content)
        elif language == 'Rust':
            result = self._analyze_rust(content)

        result['file_path'] = file_path
        result['language'] = language

        return result

    def _analyze_python(self, content: str) -> Dict[str, Any]:
        """Analyze Python code."""
        import re

        result = {
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'relationships': []
        }

        lines = content.split('\n')

        # Extract imports
        for i, line in enumerate(lines, 1):
            # from X import Y
            match = re.match(r'^\s*from\s+(\S+)\s+import\s+(.+)$', line)
            if match:
                module, names = match.groups()
                for name in names.split(','):
                    result['imports'].append({
                        'type': 'from_import',
                        'module': module,
                        'name': name.strip(),
                        'line': i
                    })
                continue

            # import X
            match = re.match(r'^\s*import\s+(.+)$', line)
            if match:
                modules = match.group(1)
                for module in modules.split(','):
                    result['imports'].append({
                        'type': 'import',
                        'module': module.strip().split(' as ')[0],
                        'line': i
                    })

        # Extract classes
        class_pattern = re.compile(r'^(\s*)class\s+(\w+)(\(([^)]+)\))?:', re.MULTILINE)
        for match in class_pattern.finditer(content):
            indent, name, _, parents = match.groups()
            line_num = content[:match.start()].count('\n') + 1

            class_info = {
                'name': name,
                'type': 'class',
                'line': line_num,
                'indent': len(indent),
                'methods': [],
                'attributes': []
            }

            if parents:
                class_info['parents'] = [p.strip() for p in parents.split(',')]
                for parent in class_info['parents']:
                    result['relationships'].append({
                        'type': 'inheritance',
                        'from': name,
                        'to': parent,
                        'line': line_num
                    })

            result['classes'].append(class_info)

        # Extract functions and methods
        func_pattern = re.compile(r'^(\s*)def\s+(\w+)\s*\(([^)]*)\)', re.MULTILINE)
        for match in func_pattern.finditer(content):
            indent, name, params = match.groups()
            line_num = content[:match.start()].count('\n') + 1

            func_info = {
                'name': name,
                'type': 'function',
                'line': line_num,
                'indent': len(indent),
                'parameters': [p.strip().split(':')[0].split('=')[0].strip()
                             for p in params.split(',') if p.strip()]
            }

            # Determine if it's a method or function
            if indent.strip() or len(indent) > 0:
                # It's likely a method
                # Find parent class
                for cls in result['classes']:
                    if cls['line'] < line_num and len(indent) > cls['indent']:
                        cls['methods'].append(func_info)
                        func_info['parent_class'] = cls['name']
                        break
            else:
                result['functions'].append(func_info)

        # Extract module-level variables
        var_pattern = re.compile(r'^([A-Z_][A-Z0-9_]*)\s*=', re.MULTILINE)
        for match in var_pattern.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            result['variables'].append({
                'name': name,
                'type': 'constant',
                'line': line_num
            })

        return result

    def _analyze_javascript(self, content: str) -> Dict[str, Any]:
        """Analyze JavaScript/TypeScript code."""
        import re

        result = {
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'relationships': []
        }

        # Extract imports
        import_pattern = re.compile(r'^\s*(?:import|const|let|var)\s+(?:{([^}]+)}|\w+)\s+(?:=\s+require\([\'"]([^\'"]+)[\'"]\)|from\s+[\'"]([^\'"]+)[\'"])', re.MULTILINE)
        for match in import_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            result['imports'].append({
                'type': 'import',
                'line': line_num
            })

        # Extract classes
        class_pattern = re.compile(r'^\s*class\s+(\w+)(?:\s+extends\s+(\w+))?', re.MULTILINE)
        for match in class_pattern.finditer(content):
            name, parent = match.groups()
            line_num = content[:match.start()].count('\n') + 1

            class_info = {
                'name': name,
                'type': 'class',
                'line': line_num,
                'methods': []
            }

            if parent:
                class_info['parent'] = parent
                result['relationships'].append({
                    'type': 'inheritance',
                    'from': name,
                    'to': parent,
                    'line': line_num
                })

            result['classes'].append(class_info)

        # Extract functions
        func_pattern = re.compile(r'^\s*(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:async\s+)?(?:\([^)]*\)|[^=])+\s*=>)', re.MULTILINE)
        for match in func_pattern.finditer(content):
            name = match.group(1) or match.group(2)
            if name:
                line_num = content[:match.start()].count('\n') + 1
                result['functions'].append({
                    'name': name,
                    'type': 'function',
                    'line': line_num
                })

        return result

    def _analyze_java(self, content: str) -> Dict[str, Any]:
        """Analyze Java code."""
        import re

        result = {
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'relationships': []
        }

        # Extract imports
        import_pattern = re.compile(r'^\s*import\s+([\w.]+);', re.MULTILINE)
        for match in import_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            result['imports'].append({
                'type': 'import',
                'module': match.group(1),
                'line': line_num
            })

        # Extract classes
        class_pattern = re.compile(r'^\s*(?:public\s+)?(?:class|interface)\s+(\w+)(?:\s+extends\s+(\w+))?(?:\s+implements\s+([\w,\s]+))?', re.MULTILINE)
        for match in class_pattern.finditer(content):
            name = match.group(1)
            parent = match.group(2)
            interfaces = match.group(3)
            line_num = content[:match.start()].count('\n') + 1

            class_info = {
                'name': name,
                'type': 'class',
                'line': line_num,
                'methods': []
            }

            if parent:
                result['relationships'].append({
                    'type': 'inheritance',
                    'from': name,
                    'to': parent,
                    'line': line_num
                })

            if interfaces:
                for iface in interfaces.split(','):
                    result['relationships'].append({
                        'type': 'implementation',
                        'from': name,
                        'to': iface.strip(),
                        'line': line_num
                    })

            result['classes'].append(class_info)

        # Extract methods
        method_pattern = re.compile(r'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:\w+)\s+(\w+)\s*\([^)]*\)', re.MULTILINE)
        for match in method_pattern.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            result['functions'].append({
                'name': name,
                'type': 'method',
                'line': line_num
            })

        return result

    def _analyze_cpp(self, content: str) -> Dict[str, Any]:
        """Analyze C++ code."""
        import re

        result = {
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'relationships': []
        }

        # Extract includes
        include_pattern = re.compile(r'^\s*#include\s+[<"]([^>"]+)[>"]', re.MULTILINE)
        for match in include_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            result['imports'].append({
                'type': 'include',
                'file': match.group(1),
                'line': line_num
            })

        # Extract classes
        class_pattern = re.compile(r'^\s*class\s+(\w+)(?:\s*:\s*(?:public|private|protected)\s+(\w+))?', re.MULTILINE)
        for match in class_pattern.finditer(content):
            name, parent = match.groups()
            line_num = content[:match.start()].count('\n') + 1

            class_info = {
                'name': name,
                'type': 'class',
                'line': line_num,
                'methods': []
            }

            if parent:
                result['relationships'].append({
                    'type': 'inheritance',
                    'from': name,
                    'to': parent,
                    'line': line_num
                })

            result['classes'].append(class_info)

        return result

    def _analyze_go(self, content: str) -> Dict[str, Any]:
        """Analyze Go code."""
        import re

        result = {
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'relationships': []
        }

        # Extract imports
        import_pattern = re.compile(r'^\s*import\s+(?:"([^"]+)"|(\([^)]+\)))', re.MULTILINE)
        for match in import_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            result['imports'].append({
                'type': 'import',
                'line': line_num
            })

        # Extract structs (Go's version of classes)
        struct_pattern = re.compile(r'^\s*type\s+(\w+)\s+struct', re.MULTILINE)
        for match in struct_pattern.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            result['classes'].append({
                'name': name,
                'type': 'struct',
                'line': line_num
            })

        # Extract functions
        func_pattern = re.compile(r'^\s*func\s+(?:\(.*?\)\s+)?(\w+)\s*\(', re.MULTILINE)
        for match in func_pattern.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            result['functions'].append({
                'name': name,
                'type': 'function',
                'line': line_num
            })

        return result

    def _analyze_rust(self, content: str) -> Dict[str, Any]:
        """Analyze Rust code."""
        import re

        result = {
            'classes': [],
            'functions': [],
            'imports': [],
            'variables': [],
            'relationships': []
        }

        # Extract use statements (imports)
        use_pattern = re.compile(r'^\s*use\s+([\w:]+)', re.MULTILINE)
        for match in use_pattern.finditer(content):
            line_num = content[:match.start()].count('\n') + 1
            result['imports'].append({
                'type': 'use',
                'module': match.group(1),
                'line': line_num
            })

        # Extract structs and enums
        struct_pattern = re.compile(r'^\s*(?:pub\s+)?(?:struct|enum)\s+(\w+)', re.MULTILINE)
        for match in struct_pattern.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            result['classes'].append({
                'name': name,
                'type': 'struct',
                'line': line_num
            })

        # Extract functions
        func_pattern = re.compile(r'^\s*(?:pub\s+)?fn\s+(\w+)\s*\(', re.MULTILINE)
        for match in func_pattern.finditer(content):
            name = match.group(1)
            line_num = content[:match.start()].count('\n') + 1
            result['functions'].append({
                'name': name,
                'type': 'function',
                'line': line_num
            })

        return result

    def extract_chunks(self, file_path: str, content: str, language: str) -> List[Dict[str, Any]]:
        """
        Extract semantic code chunks from a file.

        Args:
            file_path: File path
            content: File content
            language: Programming language

        Returns:
            List of code chunks with metadata
        """
        analysis = self.analyze_file(file_path, content, language)
        chunks = []
        lines = content.split('\n')

        # Create chunks for each class
        for cls in analysis.get('classes', []):
            chunk = self._extract_chunk_lines(
                lines,
                cls['line'] - 1,
                self._find_block_end(lines, cls['line'] - 1, language)
            )
            chunks.append({
                'type': 'class',
                'name': cls['name'],
                'start_line': cls['line'],
                'end_line': chunk['end_line'],
                'code': chunk['code'],
                'metadata': cls
            })

        # Create chunks for each function
        for func in analysis.get('functions', []):
            chunk = self._extract_chunk_lines(
                lines,
                func['line'] - 1,
                self._find_block_end(lines, func['line'] - 1, language)
            )
            chunks.append({
                'type': 'function',
                'name': func['name'],
                'start_line': func['line'],
                'end_line': chunk['end_line'],
                'code': chunk['code'],
                'metadata': func
            })

        # If no chunks found, treat whole file as one chunk
        if not chunks:
            chunks.append({
                'type': 'file',
                'name': Path(file_path).stem,
                'start_line': 1,
                'end_line': len(lines),
                'code': content,
                'metadata': analysis
            })

        return chunks

    def _extract_chunk_lines(self, lines: List[str], start: int, end: int) -> Dict[str, Any]:
        """Extract lines for a chunk."""
        chunk_lines = lines[start:end]
        return {
            'start_line': start + 1,
            'end_line': end,
            'code': '\n'.join(chunk_lines)
        }

    def _find_block_end(self, lines: List[str], start: int, language: str) -> int:
        """
        Find the end of a code block.

        Args:
            lines: Code lines
            start: Start line index
            language: Programming language

        Returns:
            End line index
        """
        if language in ('Python',):
            return self._find_python_block_end(lines, start)
        elif language in ('JavaScript', 'TypeScript', 'Java', 'C++', 'C', 'C#', 'Go', 'Rust'):
            return self._find_brace_block_end(lines, start)
        else:
            # Default: next blank line or end of file
            for i in range(start + 1, len(lines)):
                if not lines[i].strip():
                    return i
            return len(lines)

    def _find_python_block_end(self, lines: List[str], start: int) -> int:
        """Find end of Python block based on indentation."""
        if start >= len(lines):
            return len(lines)

        base_indent = len(lines[start]) - len(lines[start].lstrip())

        for i in range(start + 1, len(lines)):
            line = lines[i]
            if not line.strip():
                continue

            current_indent = len(line) - len(line.lstrip())
            if current_indent <= base_indent and line.strip():
                return i

        return len(lines)

    def _find_brace_block_end(self, lines: List[str], start: int) -> int:
        """Find end of brace-delimited block."""
        brace_count = 0
        found_start = False

        for i in range(start, len(lines)):
            line = lines[i]
            brace_count += line.count('{')
            brace_count -= line.count('}')

            if '{' in line:
                found_start = True

            if found_start and brace_count == 0:
                return i + 1

        return len(lines)
