"""
doc_templates.py
Multi-format documentation templates for TechDocAgent Advanced.

Provides templates for:
- README
- API Documentation
- Onboarding Guides
- Changelog
- Architecture Documentation
- Per-module/class/function docs
"""

from typing import Dict, List, Optional, Any


class DocTemplates:
    """
    Collection of documentation templates for various doc types.
    """

    @staticmethod
    def get_readme_template() -> str:
        """Get README template."""
        return """You are a technical documentation expert. Generate a comprehensive README.md file for this codebase.

# Context
Project Root: {project_root}
Primary Language: {primary_language}
Total Files: {file_count}
Total Lines of Code: {total_lines}

# Codebase Structure
{codebase_structure}

# Key Components
{key_components}

# Sample Code
{sample_code}

# Instructions
Generate a professional README.md with the following sections:

1. **Project Title and Description**: Create a clear, concise project title and 2-3 sentence description
2. **Features**: List 5-7 key features based on the code analysis
3. **Installation**: Provide installation instructions appropriate for the language/framework
4. **Usage**: Include basic usage examples with code snippets from the actual codebase
5. **Project Structure**: Explain the directory structure and main components
6. **Configuration**: Document any configuration files or environment variables
7. **API/Core Functions**: Highlight main functions, classes, or APIs (if applicable)
8. **Contributing**: Standard contributing guidelines
9. **License**: Placeholder for license information

Format in clean Markdown. Be specific and grounded in the actual code provided. Do NOT make up features or capabilities not present in the code.
"""

    @staticmethod
    def get_api_doc_template() -> str:
        """Get API documentation template."""
        return """You are a technical documentation expert specializing in API documentation. Generate comprehensive API documentation for this codebase.

# Context
Project: {project_name}
Language: {language}
API Type: {api_type}

# Code Analysis
{code_analysis}

# Functions/Methods
{functions_list}

# Classes/Modules
{classes_list}

# Sample Implementation
{sample_code}

# Instructions
Generate professional API documentation with the following structure:

1. **API Overview**: Brief introduction to the API and its purpose
2. **Base URL/Entry Points**: Main entry points or base URLs
3. **Authentication** (if applicable): How to authenticate
4. **Endpoints/Functions**:
   For each public function, method, or endpoint, document:
   - Name and signature
   - Purpose and description
   - Parameters (name, type, required/optional, description)
   - Return value (type and description)
   - Example usage with actual code from the codebase
   - Error handling

5. **Data Models**: Document key classes, structs, or data models
6. **Error Codes**: Common error codes and their meanings
7. **Rate Limits** (if applicable)
8. **Examples**: Complete working examples

Format as clean Markdown with code blocks. Be precise and use only information present in the provided code.
"""

    @staticmethod
    def get_onboarding_template() -> str:
        """Get onboarding guide template."""
        return """You are a developer onboarding specialist. Create a comprehensive onboarding guide for new developers joining this project.

# Context
Project: {project_name}
Tech Stack: {tech_stack}
Complexity Level: {complexity_level}
Primary Language: {primary_language}

# Codebase Overview
{codebase_overview}

# Key Components
{key_components}

# Development Setup
{setup_info}

# Instructions
Create an onboarding guide with the following sections:

1. **Welcome**: Brief welcome message and project overview
2. **Prerequisites**: Required knowledge, tools, and accounts
3. **Development Environment Setup**:
   - Step-by-step setup instructions
   - Installing dependencies
   - Environment configuration
   - Verification steps

4. **Codebase Tour**:
   - Project structure overview
   - Key directories and their purposes
   - Main entry points
   - Important files to know

5. **Development Workflow**:
   - How to run the project locally
   - How to run tests
   - Code style and conventions
   - Git workflow and branching strategy

6. **First Tasks**:
   - Suggested starter tasks for new developers
   - Where to find good first issues

7. **Key Concepts**: Important concepts, patterns, or architecture decisions
8. **Resources**: Links to additional documentation, tools, and contacts
9. **Troubleshooting**: Common issues and solutions

Format as step-by-step Markdown guide. Use actual file paths and code examples from the codebase.
"""

    @staticmethod
    def get_changelog_template() -> str:
        """Get changelog template."""
        return """You are a documentation expert. Generate a CHANGELOG.md file based on recent code changes.

# Context
Project: {project_name}
Version: {version}
Date Range: {date_range}

# Recent Changes
{recent_changes}

# Changed Files
{changed_files}

# Commit History
{commit_history}

# Instructions
Generate a CHANGELOG.md following the "Keep a Changelog" format (https://keepachangelog.com/):

Use version numbers and dates.
Group changes into categories:
- **Added**: New features
- **Changed**: Changes to existing functionality
- **Deprecated**: Soon-to-be removed features
- **Removed**: Removed features
- **Fixed**: Bug fixes
- **Security**: Security improvements

Format:
```markdown
# Changelog

## [Version] - YYYY-MM-DD

### Added
- Feature description

### Changed
- Change description

### Fixed
- Bug fix description
```

Base the changelog ONLY on the actual changes provided. Be specific and concise.
"""

    @staticmethod
    def get_architecture_template() -> str:
        """Get architecture documentation template."""
        return """You are a software architect. Create comprehensive architecture documentation for this codebase.

# Context
Project: {project_name}
Scale: {scale}
Primary Language: {primary_language}

# Codebase Structure
{codebase_structure}

# Components
{components}

# Dependencies
{dependencies}

# Instructions
Generate architecture documentation with:

1. **System Overview**: High-level description of the system
2. **Architecture Diagram**: Describe the major components and their relationships (in text/Mermaid)
3. **Component Breakdown**:
   - Purpose of each major component
   - Responsibilities
   - Dependencies
   - Key files

4. **Data Flow**: How data flows through the system
5. **Key Design Decisions**: Important architectural decisions and rationale
6. **Patterns and Principles**: Design patterns and architectural principles used
7. **External Dependencies**: Third-party libraries and services
8. **Scalability Considerations**: How the system handles scale
9. **Security Architecture**: Security measures and considerations
10. **Future Considerations**: Areas for improvement or expansion

Use Mermaid diagrams where appropriate. Be specific and grounded in the actual code.
"""

    @staticmethod
    def get_module_doc_template() -> str:
        """Get per-module/file documentation template."""
        return """You are a code documentation expert. Generate detailed documentation for this specific module/file.

# Context
File: {file_path}
Language: {language}
Lines of Code: {lines}

# Code Content
{code_content}

# Imports/Dependencies
{imports}

# Instructions
Generate module documentation with:

1. **Module Overview**: Purpose and responsibility of this module
2. **Classes**: For each class:
   - Purpose
   - Attributes
   - Methods (brief descriptions)
   - Usage example

3. **Functions**: For each function:
   - Purpose
   - Parameters
   - Return value
   - Example usage

4. **Constants/Configuration**: Important constants or configuration
5. **Dependencies**: Key dependencies and why they're used
6. **Usage Examples**: Practical examples of using this module
7. **Notes**: Any important implementation details or gotchas

Format as Markdown. Include code snippets from the actual file.
"""

    @staticmethod
    def get_function_doc_template() -> str:
        """Get per-function documentation template."""
        return """You are a code documentation expert. Generate detailed documentation for this specific function/method.

# Context
Function: {function_name}
File: {file_path}
Language: {language}

# Function Code
{function_code}

# Context Code
{context_code}

# Instructions
Generate function documentation with:

1. **Purpose**: What this function does and why it exists
2. **Signature**: Full function signature with types
3. **Parameters**: Each parameter with:
   - Name
   - Type
   - Description
   - Default value (if any)
   - Constraints/validation

4. **Return Value**: Type and description
5. **Behavior**: Detailed explanation of what the function does
6. **Examples**: 2-3 usage examples with different scenarios
7. **Edge Cases**: How it handles edge cases
8. **Exceptions**: What exceptions/errors it might raise
9. **Performance**: Time/space complexity if relevant
10. **Related Functions**: Other functions commonly used with this one

Be thorough and precise. Use only information from the provided code.
"""

    @staticmethod
    def get_test_doc_template() -> str:
        """Get test documentation template."""
        return """You are a QA documentation expert. Generate test documentation for this codebase.

# Context
Project: {project_name}
Test Framework: {test_framework}
Test Files: {test_files}

# Test Code
{test_code}

# Coverage
{coverage_info}

# Instructions
Generate test documentation with:

1. **Testing Overview**: Testing strategy and approach
2. **Test Structure**: How tests are organized
3. **Running Tests**: Commands to run tests (all, specific, with coverage)
4. **Test Categories**:
   - Unit tests
   - Integration tests
   - End-to-end tests
   - Other test types

5. **Test Coverage**: Current coverage and areas needing tests
6. **Writing Tests**: Guidelines for writing new tests
7. **Mocking/Fixtures**: How to use mocks and test fixtures
8. **CI/CD**: How tests run in CI/CD pipeline
9. **Troubleshooting**: Common test issues and solutions

Format as Markdown with code examples.
"""

    @staticmethod
    def get_deployment_template() -> str:
        """Get deployment documentation template."""
        return """You are a DevOps documentation expert. Generate deployment documentation for this project.

# Context
Project: {project_name}
Platform: {platform}
Dependencies: {dependencies}

# Configuration Files
{config_files}

# Scripts
{deployment_scripts}

# Instructions
Generate deployment documentation with:

1. **Deployment Overview**: Deployment strategy and environments
2. **Prerequisites**: Required accounts, tools, access
3. **Environment Configuration**:
   - Environment variables
   - Configuration files
   - Secrets management

4. **Build Process**: How to build the project for production
5. **Deployment Steps**: Step-by-step deployment instructions for each environment
6. **Rollback Procedure**: How to rollback if deployment fails
7. **Monitoring**: How to monitor the deployed application
8. **Troubleshooting**: Common deployment issues
9. **CI/CD Pipeline**: Automated deployment setup
10. **Infrastructure**: Infrastructure requirements and setup

Format as Markdown with clear, actionable steps.
"""

    @staticmethod
    def get_template(doc_type: str) -> Optional[str]:
        """
        Get a template by type.

        Args:
            doc_type: Type of documentation

        Returns:
            Template string or None if not found
        """
        templates = {
            'README': DocTemplates.get_readme_template(),
            'API': DocTemplates.get_api_doc_template(),
            'ONBOARDING': DocTemplates.get_onboarding_template(),
            'CHANGELOG': DocTemplates.get_changelog_template(),
            'ARCHITECTURE': DocTemplates.get_architecture_template(),
            'MODULE': DocTemplates.get_module_doc_template(),
            'FUNCTION': DocTemplates.get_function_doc_template(),
            'TEST': DocTemplates.get_test_doc_template(),
            'DEPLOYMENT': DocTemplates.get_deployment_template(),
        }

        return templates.get(doc_type.upper())

    @staticmethod
    def list_available_templates() -> List[str]:
        """Get list of available template types."""
        return [
            'README',
            'API',
            'ONBOARDING',
            'CHANGELOG',
            'ARCHITECTURE',
            'MODULE',
            'FUNCTION',
            'TEST',
            'DEPLOYMENT'
        ]

    @staticmethod
    def fill_template(template: str, context: Dict[str, Any]) -> str:
        """
        Fill a template with context data.

        Args:
            template: Template string with {placeholder} format
            context: Dictionary with placeholder values

        Returns:
            Filled template
        """
        try:
            return template.format(**context)
        except KeyError as e:
            print(f"Warning: Missing template variable {e}")
            # Fill missing variables with placeholders
            import re
            def replace_missing(match):
                key = match.group(1)
                return context.get(key, f"[{key} not provided]")

            pattern = r'\{([^}]+)\}'
            return re.sub(pattern, replace_missing, template)
