#!/usr/bin/env python3
import os


def list_files_and_contents(startpath, output_file, ignored_dirs=None, ignored_files=None):
    if ignored_dirs is None:
        ignored_dirs = ['node_modules']
    if ignored_files is None:
        ignored_files = [output_file, 'package-lock.json', '.gitignore']

    with open(output_file, 'w', encoding='utf-8') as out:
        # First, print the directory structure
        for root, dirs, files in os.walk(startpath):
            # Skip the ignored directories
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            files = [f for f in files if f not in ignored_files]

            level = root.replace(startpath, '').count(os.sep)
            indent = ' ' * 4 * (level)
            out.write(f'{indent}└── {os.path.basename(root)}/\n')

            subindent = ' ' * 4 * (level + 1)
            for f in files:
                out.write(f'{subindent}└── {f}\n')

        # Add a blank line between the structure and the contents
        out.write("\n")

        # Then, print the contents of each file
        for root, dirs, files in os.walk(startpath):
            dirs[:] = [d for d in dirs if d not in ignored_dirs]
            files = [f for f in files if f not in ignored_files]
            for f in files:
                file_path = os.path.join(root, f)
                relative_path = os.path.relpath(file_path, startpath)
                out.write(f'Contents of {relative_path}:\n\n')
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                        out.write(content + "\n")
                except UnicodeDecodeError:
                    out.write(f"Could not read {relative_path} due to encoding issues.\n")
                # Add a blank line between file contents for readability
                out.write("\n")


# Example usage:
ignored_dirs = ['node_modules', 'venv', '.git', 'dist'] 
ignored_files = ['package-lock.json', '.gitignore', 'output_structure.txt', '.DS_Store']

# Specify the output file name
output_file = 'output_structure.txt'
list_files_and_contents('.', output_file, ignored_dirs, ignored_files)

print(f"Output has been written to {output_file}")
