![Status](https://img.shields.io/badge/status-active-brightgreen)

# TechDocAgent

An agent that generates technical documentation from code.

## Overview

TechDocAgent is a project designed to automate the creation of technical documentation directly from your codebase. By leveraging advanced language models and code analysis techniques, it aims to streamline the documentation process, ensuring your project's documentation is always up-to-date and comprehensive.

## Core Capabilities & Technologies

TechDocAgent leverages the following key technologies and capabilities:

*   **Python:** The entire agent's logic, analysis components, and orchestration are built using Python.
*   **XML:** Utilized for specific aspects of documentation generation or internal data representation, ensuring structured and parseable output where required.

## Installation

To get TechDocAgent up and running, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/smilingprogrammer/TechDocAgent.git
    cd TechDocAgent
    

2.  **Install dependencies:**
    Navigate to the project's root directory and install all required Python packages using `pip`:
    ```bash
    pip install -r requirements.txt
    

## Configuration

TechDocAgent relies on a Large Language Model (LLM) for its documentation generation capabilities. You will need to provide an API key for the chosen LLM, which is expected to be Google Gemini in this configuration.

*   **`GEMINI_API_KEY`**: Set this environment variable to your actual Google Gemini API key.

    Example (for bash/zsh):
    ```bash
    export GEMINI_API_KEY="your_gemini_api_key_here"
    
    It's recommended to add this to your shell's profile file (e.g., `.bashrc`, `.zshrc`) or use a `.env` file with a package like `python-dotenv` for local development.

## Usage

Currently, the primary way to understand and interact with TechDocAgent's functionality is by exploring its comprehensive test suite. These tests serve as runnable examples demonstrating how different components of the agent work together.

*   **See `test_analysis.py` for usage examples:** This file provides a good starting point to observe how code analysis, LLM interaction, and documentation generation steps are orchestrated. You can run individual tests or examine their structure to understand the agent's workflow.

    To run the tests:
    ```bash
    pytest
    ```python
    or for a specific test file:
    ```bash
    pytest test_analysis.py
    ```python

## Test Suite Structure

The project's current development and testing efforts are organized around the following test files, which collectively demonstrate the agent's internal workings and capabilities:

*   `test_analysis.py`: Contains tests related to the code analysis components, including parsing and understanding source code.
*   `test_chunking.py`: Focuses on testing the logic for breaking down code or documentation into manageable chunks for LLM processing.
*   `test_ingestion.py`: Tests the mechanisms for ingesting various forms of input data into the agent.
*   `test_llm.py`: Dedicated to testing interactions with the Large Language Model, ensuring correct prompting and response handling.
*   `test_llm_json.py`: Specifically tests scenarios where LLM interactions involve JSON-formatted inputs or outputs.
*   `test_pipeline.py`: Provides end-to-end tests for the entire documentation generation pipeline, from code input to final output.
*   `test_prompt_fill.py`: Tests the templating and filling mechanisms for constructing prompts sent to the LLM.