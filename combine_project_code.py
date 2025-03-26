import os

# Define paths
docker_compose_file = "docker-compose.yaml"
k8s_directory = "k8s/"
output_file = "combined_output.txt"

def read_file_content(file_path):
    """Reads the content of a file and returns it as a string."""
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            return file.read()
    except Exception as e:
        return f"Error reading {file_path}: {str(e)}"

def main():
    """Reads specified files and combines their content into a single text file."""
    with open(output_file, "w", encoding="utf-8") as out_file:
        
        # Process docker-compose.yaml
        if os.path.exists(docker_compose_file):
            out_file.write(f"---------\n{docker_compose_file} code\n----------\n")
            out_file.write(read_file_content(docker_compose_file) + "\n\n")
        
        # Process files inside k8s directory
        if os.path.exists(k8s_directory) and os.path.isdir(k8s_directory):
            for filename in sorted(os.listdir(k8s_directory)):
                file_path = os.path.join(k8s_directory, filename)
                if os.path.isfile(file_path):
                    out_file.write(f"---------\n{k8s_directory}{filename} code\n----------\n")
                    out_file.write(read_file_content(file_path) + "\n\n")
        
    print(f"Combined file created: {output_file}")

if __name__ == "__main__":
    main()
