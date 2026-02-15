import os
import re
import shutil

def deconsolidate_file(input_filename="consolidated_project.txt", dry_run=True):
    if not os.path.exists(input_filename):
        print(f"Error: {input_filename} not found.")
        return

    print(f"{'--- DRY RUN ACTIVE: No changes will be made ---' if dry_run else '--- LIVE MODE: Restoring files ---'}\n")

    with open(input_filename, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to capture the filepath and the content
    pattern = r"={80}\n FILE: (.*?)\n={80}\n\n(.*?)(?=\n={80}\n FILE: |\Z)"
    matches = re.findall(pattern, content, re.DOTALL)

    if not matches:
        print("No file markers found. Please check the format of your consolidated file.")
        return

    for filepath, file_content in matches:
        filepath = filepath.strip()
        directory = os.path.dirname(filepath)
        
        # Action: Create Directory
        if directory and not os.path.exists(directory):
            if dry_run:
                print(f"[DRY RUN] Would create directory: {directory}")
            else:
                os.makedirs(directory)
                print(f"Created directory: {directory}")

        # Action: Backup Existing File
        if os.path.exists(filepath):
            backup_path = f"{filepath}_backup"
            if dry_run:
                print(f"[DRY RUN] Would backup: {filepath} -> {backup_path}")
            else:
                shutil.move(filepath, backup_path)
                print(f"Backed up: {filepath} -> {backup_path}")

        # Action: Write File
        if dry_run:
            print(f"[DRY RUN] Would write {len(file_content)} characters to: {filepath}")
        else:
            try:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(file_content.rstrip() + "\n")
                print(f"Restored: {filepath}")
            except Exception as e:
                print(f"Failed to write {filepath}: {e}")

    if dry_run:
        print("\nDry run complete. Change 'dry_run=False' in the script to apply changes.")
    else:
        print("\nDe-consolidation complete!")

if __name__ == "__main__":
    # Toggle this to False to actually perform the file operations
    deconsolidate_file(dry_run=False)
