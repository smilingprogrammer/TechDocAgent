"""
prompts.py
Module for prompt templates for documentation generation.
"""

README_PROMPT = """
You are a technical writer. Write a comprehensive README for the following project.

Project Name: {project_name}
Description: {project_description}
Main Features:
{features_list}

Codebase Structure:
{code_structure}

Usage Instructions:
{usage_examples}

Include installation steps, usage examples, and any other relevant information.
"""

API_DOCS_PROMPT = """
You are a technical writer. Write API documentation for the following codebase.

API Endpoints:
{api_endpoints}

Descriptions:
{descriptions}

Include request/response examples and authentication details if available.
""" 