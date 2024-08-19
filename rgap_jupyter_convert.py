#!/usr/bin/env python3
import argparse
import os

import nbformat
from nbconvert import ScriptExporter


def convert_notebook_to_script(notebook_path, output_dir="scripts"):
    # Load the notebook
    with open(notebook_path) as f:
        notebook = nbformat.read(f, as_version=4)

    # Create a script exporter
    script_exporter = ScriptExporter()

    # Convert the notebook to a script
    (script, resources) = script_exporter.from_notebook_node(notebook)

    # Determine the output script file name
    base_name = os.path.splitext(os.path.basename(notebook_path))[0]
    script_filename = os.path.join(output_dir, base_name + ".py")

    # Ensure the output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Save the script
    with open(script_filename, "w") as f:
        f.write(script)

    print(f"Notebook converted to script: {script_filename}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Convert a Jupyter notebook to a Python script."
    )
    parser.add_argument("notebook", help="Path to the Jupyter notebook file (.ipynb)")

    args = parser.parse_args()
    convert_notebook_to_script(args.notebook)
