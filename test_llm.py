from techdocagent.pipeline import process_codebase
from techdocagent.prompts import fill_readme_prompt
from techdocagent.llm import generate_documentation
from techdocagent.output import output_documentation
import os
from dotenv import load_dotenv

if __name__ == "__main__":
    load_dotenv()
    # Ensure GOOGLE_API_KEY is set
    if not os.environ.get('GEMINI_API_KEY'):
        print("ERROR: Please set the GOOGLE_API_KEY environment variable before running this script.")
        exit(1)
    root = "."
    processed = process_codebase(root)
    prompt = fill_readme_prompt(processed, project_name="TechDocAgent", project_description="An agent that generates technical documentation from code.")
    print("\nSending prompt to Gemini...\n")
    doc = generate_documentation(prompt)
    output_documentation(doc, output_path="README.md")