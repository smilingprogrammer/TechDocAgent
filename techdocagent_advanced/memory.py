"""
memory.py
Memory management system for TechDocAgent Advanced.

Provides:
- Persistent storage of codebase summaries and metadata
- User feedback storage and retrieval
- Change tracking with file hashes
- Session context management
"""

import json
import hashlib
import sqlite3
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class MemoryManager:
    """
    Manages persistent memory for the documentation agent.

    Features:
    - Store codebase metadata and file hashes
    - Track documentation generation history
    - Store and retrieve user feedback
    - Maintain session context
    """

    def __init__(self, db_path: str = ".techdoc_memory.db"):
        """
        Initialize memory manager with SQLite database.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        self._initialize_schema()

    def _initialize_schema(self):
        """Create database tables if they don't exist."""
        cursor = self.conn.cursor()

        # Files table: track file metadata and hashes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                content_hash TEXT NOT NULL,
                language TEXT,
                last_analyzed TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # Documentation table: track generated documentation
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS documentation (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_type TEXT NOT NULL,
                file_path TEXT,
                content TEXT NOT NULL,
                version_hash TEXT,
                generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        # Feedback table: store user feedback
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                doc_id INTEGER,
                feedback_type TEXT NOT NULL,
                rating INTEGER,
                comment TEXT,
                correction TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (doc_id) REFERENCES documentation (id)
            )
        """)

        # Sessions table: track analysis sessions
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                ended_at TIMESTAMP,
                context TEXT
            )
        """)

        # Changes table: track codebase changes
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS changes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT NOT NULL,
                old_hash TEXT,
                new_hash TEXT,
                change_type TEXT NOT NULL,
                detected_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """)

        self.conn.commit()

    def compute_file_hash(self, content: str) -> str:
        """Compute SHA256 hash of file content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()

    def store_file_metadata(self, file_path: str, content: str, language: str, metadata: Optional[Dict] = None):
        """
        Store or update file metadata and hash.

        Args:
            file_path: Path to the file
            content: File content
            language: Detected programming language
            metadata: Additional metadata as dictionary
        """
        content_hash = self.compute_file_hash(content)
        metadata_json = json.dumps(metadata) if metadata else None

        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO files (file_path, content_hash, language, metadata)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(file_path) DO UPDATE SET
                content_hash = excluded.content_hash,
                language = excluded.language,
                last_analyzed = CURRENT_TIMESTAMP,
                metadata = excluded.metadata
        """, (file_path, content_hash, language, metadata_json))

        self.conn.commit()

    def get_file_metadata(self, file_path: str) -> Optional[Dict]:
        """
        Retrieve stored metadata for a file.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with file metadata or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM files WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()

        if row:
            result = dict(row)
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            return result
        return None

    def has_file_changed(self, file_path: str, current_content: str) -> bool:
        """
        Check if a file has changed since last analysis.

        Args:
            file_path: Path to the file
            current_content: Current file content

        Returns:
            True if file has changed or is new, False otherwise
        """
        stored = self.get_file_metadata(file_path)
        if not stored:
            return True

        current_hash = self.compute_file_hash(current_content)
        return current_hash != stored['content_hash']

    def store_documentation(self, doc_type: str, content: str, file_path: Optional[str] = None,
                          version_hash: Optional[str] = None, metadata: Optional[Dict] = None) -> int:
        """
        Store generated documentation.

        Args:
            doc_type: Type of documentation (e.g., 'README', 'API', 'CHANGELOG')
            content: Documentation content
            file_path: Associated file path (if applicable)
            version_hash: Git commit hash or version identifier
            metadata: Additional metadata

        Returns:
            ID of stored documentation
        """
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute("""
            INSERT INTO documentation (doc_type, file_path, content, version_hash, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (doc_type, file_path, content, version_hash, metadata_json))

        self.conn.commit()
        return cursor.lastrowid

    def get_latest_documentation(self, doc_type: str, file_path: Optional[str] = None) -> Optional[Dict]:
        """
        Retrieve the most recent documentation of a specific type.

        Args:
            doc_type: Type of documentation
            file_path: Optional file path filter

        Returns:
            Documentation dictionary or None
        """
        cursor = self.conn.cursor()

        if file_path:
            cursor.execute("""
                SELECT * FROM documentation
                WHERE doc_type = ? AND file_path = ?
                ORDER BY generated_at DESC LIMIT 1
            """, (doc_type, file_path))
        else:
            cursor.execute("""
                SELECT * FROM documentation
                WHERE doc_type = ?
                ORDER BY generated_at DESC LIMIT 1
            """, (doc_type,))

        row = cursor.fetchone()
        if row:
            result = dict(row)
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            return result
        return None

    def store_feedback(self, doc_id: int, feedback_type: str, rating: Optional[int] = None,
                      comment: Optional[str] = None, correction: Optional[str] = None):
        """
        Store user feedback for generated documentation.

        Args:
            doc_id: ID of documentation being reviewed
            feedback_type: Type of feedback ('rating', 'correction', 'comment')
            rating: Numerical rating (1-5)
            comment: User comment
            correction: User-provided correction
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO feedback (doc_id, feedback_type, rating, comment, correction)
            VALUES (?, ?, ?, ?, ?)
        """, (doc_id, feedback_type, rating, comment, correction))

        self.conn.commit()

    def get_feedback_for_doc(self, doc_id: int) -> List[Dict]:
        """
        Retrieve all feedback for a specific documentation.

        Args:
            doc_id: Documentation ID

        Returns:
            List of feedback dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM feedback WHERE doc_id = ? ORDER BY created_at DESC", (doc_id,))
        return [dict(row) for row in cursor.fetchall()]

    def get_feedback_summary(self, doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get summary statistics for feedback.

        Args:
            doc_type: Optional filter by documentation type

        Returns:
            Dictionary with feedback statistics
        """
        cursor = self.conn.cursor()

        if doc_type:
            cursor.execute("""
                SELECT
                    COUNT(*) as total_feedback,
                    AVG(rating) as avg_rating,
                    COUNT(CASE WHEN correction IS NOT NULL THEN 1 END) as corrections_count
                FROM feedback f
                JOIN documentation d ON f.doc_id = d.id
                WHERE d.doc_type = ?
            """, (doc_type,))
        else:
            cursor.execute("""
                SELECT
                    COUNT(*) as total_feedback,
                    AVG(rating) as avg_rating,
                    COUNT(CASE WHEN correction IS NOT NULL THEN 1 END) as corrections_count
                FROM feedback
            """)

        row = cursor.fetchone()
        return dict(row) if row else {}

    def track_change(self, file_path: str, old_hash: Optional[str], new_hash: str,
                    change_type: str, metadata: Optional[Dict] = None):
        """
        Record a change in the codebase.

        Args:
            file_path: Path to changed file
            old_hash: Previous content hash (None for new files)
            new_hash: New content hash
            change_type: Type of change ('added', 'modified', 'deleted')
            metadata: Additional change metadata
        """
        cursor = self.conn.cursor()
        metadata_json = json.dumps(metadata) if metadata else None

        cursor.execute("""
            INSERT INTO changes (file_path, old_hash, new_hash, change_type, metadata)
            VALUES (?, ?, ?, ?, ?)
        """, (file_path, old_hash, new_hash, change_type, metadata_json))

        self.conn.commit()

    def get_recent_changes(self, limit: int = 100) -> List[Dict]:
        """
        Get recent changes to the codebase.

        Args:
            limit: Maximum number of changes to return

        Returns:
            List of change dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT * FROM changes
            ORDER BY detected_at DESC
            LIMIT ?
        """, (limit,))

        results = []
        for row in cursor.fetchall():
            result = dict(row)
            if result.get('metadata'):
                result['metadata'] = json.loads(result['metadata'])
            results.append(result)
        return results

    def create_session(self, session_id: str, context: Optional[Dict] = None) -> int:
        """
        Create a new analysis session.

        Args:
            session_id: Unique session identifier
            context: Session context dictionary

        Returns:
            Session ID
        """
        cursor = self.conn.cursor()
        context_json = json.dumps(context) if context else None

        cursor.execute("""
            INSERT INTO sessions (session_id, context)
            VALUES (?, ?)
        """, (session_id, context_json))

        self.conn.commit()
        return cursor.lastrowid

    def close_session(self, session_id: str):
        """Mark a session as ended."""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE sessions
            SET ended_at = CURRENT_TIMESTAMP
            WHERE session_id = ?
        """, (session_id,))
        self.conn.commit()

    def get_all_file_paths(self) -> List[str]:
        """Get all tracked file paths."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT file_path FROM files")
        return [row[0] for row in cursor.fetchall()]

    def clear_old_data(self, days: int = 30):
        """
        Clear old data from the database.

        Args:
            days: Remove data older than this many days
        """
        cursor = self.conn.cursor()

        # Keep recent documentation and feedback, but archive old changes
        cursor.execute("""
            DELETE FROM changes
            WHERE detected_at < datetime('now', '-' || ? || ' days')
        """, (days,))

        self.conn.commit()

    def close(self):
        """Close the database connection."""
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
