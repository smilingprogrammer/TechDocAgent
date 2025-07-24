"""
output.py
Module for output management: prints or writes generated documentation to file.
"""

def output_documentation(doc_text, output_path="README.md"):
    """
    Write the documentation to the specified file (default: README.md).
    """
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(doc_text)
    print(f"Documentation saved to {output_path}") 