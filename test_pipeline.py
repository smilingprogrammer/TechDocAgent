from techdocagent.pipeline import process_codebase

if __name__ == "__main__":
    root = "."
    results = process_codebase(root)
    for file_result in results:
        meta = file_result['file_metadata']
        print(f"\nFile: {meta['file_path']} ({meta['language']}, {meta['size_bytes']} bytes)")
        print(f"Chunks: {len(file_result['chunks'])}")
        for chunk in file_result['chunks']:
            print(f"  - Type: {chunk['type']}, Name: {chunk['name']}, Lines: {chunk['start_line']}-{chunk['end_line']}") 