"""
pipeline.py
High-level pipeline for processing a codebase: ingestion, analysis, and chunking, with JSON-based LLM prompt and output.
"""
from techdocagent.ingestion import ingest_codebase
from techdocagent.analysis import analyze_file
from techdocagent.chunking import chunk_code
# from techdocagent.prompts import build_json_prompt, build_llm_prompt_json_in_json_out, parse_llm_json_output
from techdocagent.llm import generate_documentation


def process_codebase(root_path):
    """
    Process the codebase at root_path:
      - Ingest code files
      - Analyze each file for language and metadata
      - Chunk each file into logical code units
    Returns a list of dicts with file metadata and code chunks.
    """
    code_files = ingest_codebase(root_path)
    results = []
    for file_path in code_files:
        metadata = analyze_file(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chunks = chunk_code(content, metadata['language'])
        results.append({
            'file_metadata': metadata,
            'chunks': chunks
        })
    return results


def process_codebase_json(root_path, project_name="Project", project_description="A codebase."):
    """
    Process the codebase at root_path:
      - Ingest code files
      - Analyze each file for language and metadata
      - Chunk each file into logical code units
      - Build a JSON prompt for the LLM
      - Send the prompt to the LLM and parse the JSON output
    Returns the parsed JSON result from the LLM.
    """
    code_files = ingest_codebase(root_path)
    results = []
    for file_path in code_files:
        metadata = analyze_file(file_path)
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        chunks = chunk_code(content, metadata['language'])
        results.append({
            'file_metadata': metadata,
            'chunks': chunks
        })
    # Build JSON prompt
    prompt_json = build_json_prompt(results, project_name=project_name, project_description=project_description)
    llm_prompt = build_llm_prompt_json_in_json_out(prompt_json)
    # Send to LLM and parse JSON output
    llm_output = generate_documentation(llm_prompt)
    parsed = parse_llm_json_output(llm_output)
    return parsed 