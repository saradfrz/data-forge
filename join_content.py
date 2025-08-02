from pathlib import Path

def save_files_with_content(file_paths, output_file):
    with open(output_file, "w", encoding="utf-8") as out:
        for file_path in file_paths:
            path = Path(file_path).resolve()
            try:
                relative_path = path.relative_to(Path.cwd())
            except ValueError:
                relative_path = path  # fallback if file is outside current working directory

            try:
                with path.open("r", encoding="utf-8") as file:
                    content = file.read()
            except Exception as e:
                content = f"[Error reading file: {e}]"

            out.write("=" * 17 + "\n")
            out.write(str(relative_path) + "\n")
            out.write("-" * 29 + "\n")
            out.write(content + "\n")
            out.write("=" * 17 + "\n")

# Example usage:
if __name__ == "__main__":
    # Replace with your list of file paths
    files = [
        "docker-compose.yaml",
        ".makefile",
        "jupyter/Dockerfile"
    ]
    save_files_with_content(files, "output.txt")
