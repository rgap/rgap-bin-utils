#!/usr/bin/env python3
import os
import sys

def parse_structure(input_str):
    lines = input_str.strip().splitlines()
    structure = {}
    stack = [(structure, 0)]  # Stack holds (current level, current indent)

    for line in lines:
        indent = len(line) - len(line.lstrip(' │└├'))
        name = line.strip(' │└├─')
        
        if name.endswith('/'):
            folder_name = name.rstrip('/')
            new_folder = {}
            while stack and indent <= stack[-1][1]:
                stack.pop()
            current_level = stack[-1][0]
            current_level[folder_name] = new_folder
            stack.append((new_folder, indent))
        else:
            file_name = name
            current_level = stack[-1][0]
            current_level[file_name] = None

    return structure

def create_structure(base_path, structure):
    for name, content in structure.items():
        path = os.path.join(base_path, name)
        print(f"Attempting to create: {path}")  # Debug statement
        if isinstance(content, dict):
            try:
                os.makedirs(path, exist_ok=True)
                print(f"Directory created: {path}")
            except Exception as e:
                print(f"Failed to create directory: {path}. Error: {e}")
            create_structure(path, content)
        else:
            try:
                with open(path, 'w') as f:
                    print(f"File created: {path}")
            except Exception as e:
                print(f"Failed to create file: {path}. Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rgap_create_tree_structure.py <structure_file>")
        sys.exit(1)
    
    structure_file = sys.argv[1]
    
    # Check if the structure file exists
    if not os.path.exists(structure_file):
        print(f"Structure file '{structure_file}' not found.")
        sys.exit(1)

    # Read from the provided text file
    with open(structure_file, 'r') as file:
        input_str = file.read()
    
    folder_structure = parse_structure(input_str)
    
    # Print the parsed structure for debugging
    print("Parsed Structure:")
    print(folder_structure)
    
    base_path = os.getcwd()
    create_structure(base_path, folder_structure)
    
    print("Folder and file structure creation process completed.")
