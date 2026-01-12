import os

SOURCE_DIR = "."          # directory to scan (current dir by default)
OUTPUT_FILE = "main.txt"
EXTENSIONS = (".py", ".kv")

def combine_files(source_dir, output_file):
    with open(output_file, "w", encoding="utf-8") as out:
        for root, _, files in os.walk(source_dir):
            for filename in sorted(files):
                if filename.endswith(EXTENSIONS):
                    filepath = os.path.join(root, filename)

                    out.write("\n\n\n")
                    out.write(f"===== {filepath} =====\n\n")

                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            out.write(f.read())
                    except Exception as e:
                        out.write(f"# ERROR READING FILE: {e}\n")

    print(f"Combined file written to: {output_file}")

if __name__ == "__main__":
    combine_files(SOURCE_DIR, OUTPUT_FILE)