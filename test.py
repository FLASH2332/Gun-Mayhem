import os

def write_file_contents(root_dir, sub_dirs, root_files=None, output_file="out.txt"):
    output_path = os.path.join(root_dir, output_file)
    print(output_path)

    with open(output_path, "w", encoding="utf-8") as out_file:
        # Handle root-level files
        if root_files:
            for file in root_files:
                file_path = os.path.join(root_dir, file)
                relative_path = os.path.relpath(file_path, root_dir).replace("\\", "/")
                out_file.write(f"/{relative_path}:\n")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        contents = f.read()
                    out_file.write(contents)
                except Exception as e:
                    out_file.write(f"[Error reading file: {e}]")
                out_file.write("\n\n")

        # Handle subdirectories
        for sub_dir in sub_dirs:
            full_sub_dir = os.path.join(root_dir, sub_dir.lstrip("/"))
            for dirpath, _, filenames in os.walk(full_sub_dir):
                for filename in filenames:
                    file_path = os.path.join(dirpath, filename)
                    relative_path = os.path.relpath(file_path, root_dir).replace("\\", "/")
                    
                    out_file.write(f"/{relative_path}:\n")
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            contents = f.read()
                        out_file.write(contents)
                    except Exception as e:
                        out_file.write(f"[Error reading file: {e}]")
                    out_file.write("\n\n")

# Example usage
root = "C:/Users/jayad/Desktop/PROJECTS/Gun-Mayhem"
dirs = ["/include", "/src"]
files = ["main.cpp"]  # files at root to include
write_file_contents(root, dirs, files)
