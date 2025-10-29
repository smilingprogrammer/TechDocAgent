"""
feedback.py
User feedback loop system for TechDocAgent Advanced.

Provides:
- Collect and store user feedback
- Rating system for generated docs
- User corrections and suggestions
- Feedback analysis and learning
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum


class FeedbackType(Enum):
    """Types of feedback."""
    RATING = "rating"
    CORRECTION = "correction"
    COMMENT = "comment"
    SUGGESTION = "suggestion"
    ERROR_REPORT = "error_report"


class FeedbackManager:
    """
    Manages user feedback for documentation quality improvement.

    Features:
    - Collect structured feedback
    - Analyze feedback patterns
    - Extract improvement suggestions
    - Track feedback trends
    """

    def __init__(self, memory_manager):
        """
        Initialize feedback manager.

        Args:
            memory_manager: MemoryManager instance for storage
        """
        self.memory_manager = memory_manager

    def collect_rating(self, doc_id: int, rating: int, comment: Optional[str] = None) -> bool:
        """
        Collect a rating for generated documentation.

        Args:
            doc_id: Documentation ID
            rating: Rating from 1-5
            comment: Optional comment

        Returns:
            True if successful
        """
        if not 1 <= rating <= 5:
            print("Rating must be between 1 and 5")
            return False

        try:
            self.memory_manager.store_feedback(
                doc_id=doc_id,
                feedback_type=FeedbackType.RATING.value,
                rating=rating,
                comment=comment
            )
            return True
        except Exception as e:
            print(f"Error storing rating: {e}")
            return False

    def collect_correction(self, doc_id: int, correction: str, comment: Optional[str] = None) -> bool:
        """
        Collect a user correction for documentation.

        Args:
            doc_id: Documentation ID
            correction: Corrected text
            comment: Optional explanation

        Returns:
            True if successful
        """
        try:
            self.memory_manager.store_feedback(
                doc_id=doc_id,
                feedback_type=FeedbackType.CORRECTION.value,
                correction=correction,
                comment=comment
            )
            return True
        except Exception as e:
            print(f"Error storing correction: {e}")
            return False

    def collect_comment(self, doc_id: int, comment: str) -> bool:
        """
        Collect a general comment about documentation.

        Args:
            doc_id: Documentation ID
            comment: User comment

        Returns:
            True if successful
        """
        try:
            self.memory_manager.store_feedback(
                doc_id=doc_id,
                feedback_type=FeedbackType.COMMENT.value,
                comment=comment
            )
            return True
        except Exception as e:
            print(f"Error storing comment: {e}")
            return False

    def collect_suggestion(self, doc_id: int, suggestion: str) -> bool:
        """
        Collect a user suggestion for improvement.

        Args:
            doc_id: Documentation ID
            suggestion: Improvement suggestion

        Returns:
            True if successful
        """
        try:
            self.memory_manager.store_feedback(
                doc_id=doc_id,
                feedback_type=FeedbackType.SUGGESTION.value,
                comment=suggestion
            )
            return True
        except Exception as e:
            print(f"Error storing suggestion: {e}")
            return False

    def report_error(self, doc_id: int, error_description: str) -> bool:
        """
        Report an error in generated documentation.

        Args:
            doc_id: Documentation ID
            error_description: Description of the error

        Returns:
            True if successful
        """
        try:
            self.memory_manager.store_feedback(
                doc_id=doc_id,
                feedback_type=FeedbackType.ERROR_REPORT.value,
                comment=error_description
            )
            return True
        except Exception as e:
            print(f"Error storing error report: {e}")
            return False

    def get_feedback_for_doc(self, doc_id: int) -> List[Dict]:
        """
        Get all feedback for a specific documentation.

        Args:
            doc_id: Documentation ID

        Returns:
            List of feedback entries
        """
        return self.memory_manager.get_feedback_for_doc(doc_id)

    def analyze_feedback(self, doc_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Analyze feedback patterns and trends.

        Args:
            doc_type: Optional filter by documentation type

        Returns:
            Analysis results
        """
        summary = self.memory_manager.get_feedback_summary(doc_type)

        analysis = {
            'summary': summary,
            'insights': []
        }

        # Add insights based on feedback
        avg_rating = summary.get('avg_rating')
        if avg_rating:
            if avg_rating < 3.0:
                analysis['insights'].append("Low average rating - documentation quality needs improvement")
            elif avg_rating >= 4.0:
                analysis['insights'].append("High average rating - documentation quality is good")

        corrections_count = summary.get('corrections_count', 0)
        if corrections_count > 5:
            analysis['insights'].append(f"High number of corrections ({corrections_count}) - review prompt templates")

        return analysis

    def get_common_corrections(self, doc_type: Optional[str] = None, limit: int = 10) -> List[Dict]:
        """
        Get most common corrections to identify improvement areas.

        Args:
            doc_type: Optional filter by documentation type
            limit: Maximum number of corrections to return

        Returns:
            List of common corrections
        """
        # This would need more sophisticated text analysis
        # For now, just return recent corrections
        cursor = self.memory_manager.conn.cursor()

        if doc_type:
            cursor.execute("""
                SELECT f.correction, f.comment, d.doc_type, f.created_at
                FROM feedback f
                JOIN documentation d ON f.doc_id = d.id
                WHERE f.correction IS NOT NULL AND d.doc_type = ?
                ORDER BY f.created_at DESC
                LIMIT ?
            """, (doc_type, limit))
        else:
            cursor.execute("""
                SELECT f.correction, f.comment, d.doc_type, f.created_at
                FROM feedback f
                JOIN documentation d ON f.doc_id = d.id
                WHERE f.correction IS NOT NULL
                ORDER BY f.created_at DESC
                LIMIT ?
            """, (limit,))

        results = []
        for row in cursor.fetchall():
            results.append({
                'correction': row[0],
                'comment': row[1],
                'doc_type': row[2],
                'created_at': row[3]
            })

        return results

    def get_improvement_suggestions(self) -> List[str]:
        """
        Generate improvement suggestions based on feedback analysis.

        Returns:
            List of actionable suggestions
        """
        suggestions = []
        analysis = self.analyze_feedback()

        # Based on ratings
        avg_rating = analysis['summary'].get('avg_rating')
        if avg_rating and avg_rating < 3.5:
            suggestions.append("Consider revising prompt templates for better documentation quality")
            suggestions.append("Review user corrections to identify common issues")

        # Based on corrections
        corrections = self.get_common_corrections(limit=5)
        if len(corrections) > 3:
            suggestions.append("Multiple corrections detected - analyze patterns and update prompts")

        # Based on error reports
        cursor = self.memory_manager.conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM feedback
            WHERE feedback_type = ?
        """, (FeedbackType.ERROR_REPORT.value,))
        error_count = cursor.fetchone()[0]

        if error_count > 5:
            suggestions.append(f"{error_count} errors reported - review post-processing and validation")

        if not suggestions:
            suggestions.append("Documentation quality appears good - continue monitoring feedback")

        return suggestions

    def create_feedback_report(self, doc_type: Optional[str] = None) -> str:
        """
        Create a formatted feedback report.

        Args:
            doc_type: Optional filter by documentation type

        Returns:
            Formatted report string
        """
        analysis = self.analyze_feedback(doc_type)
        corrections = self.get_common_corrections(doc_type, limit=5)
        suggestions = self.get_improvement_suggestions()

        report = []
        report.append("=" * 60)
        report.append("FEEDBACK REPORT")
        if doc_type:
            report.append(f"Documentation Type: {doc_type}")
        report.append("=" * 60)
        report.append("")

        # Summary
        summary = analysis['summary']
        report.append("SUMMARY")
        report.append("-" * 60)
        report.append(f"Total Feedback: {summary.get('total_feedback', 0)}")
        if summary.get('avg_rating'):
            report.append(f"Average Rating: {summary['avg_rating']:.2f}/5.0")
        report.append(f"Corrections: {summary.get('corrections_count', 0)}")
        report.append("")

        # Insights
        if analysis['insights']:
            report.append("INSIGHTS")
            report.append("-" * 60)
            for insight in analysis['insights']:
                report.append(f"- {insight}")
            report.append("")

        # Recent Corrections
        if corrections:
            report.append("RECENT CORRECTIONS")
            report.append("-" * 60)
            for i, correction in enumerate(corrections, 1):
                report.append(f"{i}. {correction['doc_type']}")
                if correction.get('correction'):
                    report.append(f"   Correction: {correction['correction'][:100]}...")
                if correction.get('comment'):
                    report.append(f"   Comment: {correction['comment'][:100]}...")
                report.append("")

        # Suggestions
        if suggestions:
            report.append("IMPROVEMENT SUGGESTIONS")
            report.append("-" * 60)
            for i, suggestion in enumerate(suggestions, 1):
                report.append(f"{i}. {suggestion}")
            report.append("")

        report.append("=" * 60)

        return "\n".join(report)

    def apply_corrections_to_prompt(self, doc_type: str, original_prompt: str) -> str:
        """
        Apply learned corrections to improve a prompt.

        Args:
            doc_type: Documentation type
            original_prompt: Original prompt template

        Returns:
            Enhanced prompt with corrections applied
        """
        corrections = self.get_common_corrections(doc_type, limit=10)

        if not corrections:
            return original_prompt

        # Add a section to the prompt about common issues
        enhancement = "\n\nIMPORTANT - Based on user feedback, please avoid these common issues:\n"
        for i, correction in enumerate(corrections[:5], 1):
            if correction.get('comment'):
                enhancement += f"{i}. {correction['comment']}\n"

        return original_prompt + enhancement

    def interactive_feedback_session(self, doc_id: int, doc_content: str) -> Dict[str, Any]:
        """
        Conduct an interactive feedback session (for CLI/UI integration).

        Args:
            doc_id: Documentation ID
            doc_content: Documentation content

        Returns:
            Collected feedback dictionary
        """
        print("\n" + "=" * 60)
        print("DOCUMENTATION FEEDBACK")
        print("=" * 60)
        print("\nGenerated Documentation:")
        print("-" * 60)
        print(doc_content[:500])  # Show preview
        if len(doc_content) > 500:
            print(f"... ({len(doc_content) - 500} more characters)")
        print("-" * 60)

        feedback_data = {
            'doc_id': doc_id,
            'rating': None,
            'comments': [],
            'corrections': [],
            'suggestions': []
        }

        # This is a placeholder for interactive feedback
        # In a real implementation, this would use input() or a UI
        print("\nFeedback collected successfully!")

        return feedback_data
