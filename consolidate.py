import os

def consolidate_files(output_filename="consolidated_project.txt"):
    target_dirs = ['.', './screens']
    valid_extensions = ('.py', '.kv','.spec')
    # Files to explicitly ignore
    ignored_files = [output_filename, 'consolidate.py', 'deconsolidate.py']
    
    with open(output_filename, 'w', encoding='utf-8') as outfile:
        # --- PART 1: Generate Directory Map ---
        outfile.write(f"{'#'*80}\n")
        outfile.write(f" PROJECT STRUCTURE MAP\n")
        outfile.write(f"{'#'*80}\n\n")
        
        for directory in target_dirs:
            if os.path.exists(directory):
                outfile.write(f"{directory}/\n")
                # Filter out ignored files and backup files for the map
                files = [f for f in os.listdir(directory) 
                         if f.endswith(valid_extensions) 
                         and f not in ignored_files 
                         and not f.endswith('_backup')]
                
                for i, filename in enumerate(sorted(files)):
                    connector = "└── " if i == len(files) - 1 else "├── "
                    outfile.write(f"    {connector}{filename}\n")
            else:
                outfile.write(f"{directory} (Not Found)\n")
        
        outfile.write("\n\n")

        # --- PART 2: Consolidate File Contents ---
        for directory in target_dirs:
            if not os.path.exists(directory):
                continue
                
            for filename in sorted(os.listdir(directory)):
                filepath = os.path.join(directory, filename)
                
                # Logic: Must be .py/.kv AND not an ignored file AND not a backup
                is_valid_ext = filename.endswith(valid_extensions)
                is_ignored = filename in ignored_files
                is_backup = filename.endswith('_backup')

                if is_valid_ext and not is_ignored and not is_backup:
                    try:
                        with open(filepath, 'r', encoding='utf-8') as infile:
                            content = infile.read()
                            
                            outfile.write(f"\n{'='*80}\n")
                            outfile.write(f" FILE: {filepath}\n")
                            outfile.write(f"{'='*80}\n\n")
                            
                            outfile.write(content)
                            outfile.write("\n\n")
                            
                            print(f"Included: {filepath}")
                    except Exception as e:
                        print(f"Error reading {filepath}: {e}")

    print(f"\nDone! Clean consolidation saved to {output_filename}")

if __name__ == "__main__":
    consolidate_files()
