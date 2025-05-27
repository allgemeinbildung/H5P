import os
import shutil
import zipfile
from pathlib import Path

def process_h5p_files(h5p_folder_path_str: str):
    """
    Processes .h5p files in a specified folder. For each .h5p file,
    it copies a template folder, renames it to match the .h5p file name,
    and extracts the .h5p content into a 'h5p-folder' subdirectory
    within the copied template.
    """
    try:
        # Resolve the path to get an absolute and canonical path
        h5p_dir = Path(h5p_folder_path_str).resolve()
    except Exception as e:
        print(f"Error: The provided path '{h5p_folder_path_str}' is invalid: {e}")
        return

    # Check if the provided path is a directory
    if not h5p_dir.is_dir():
        print(f"Error: The path '{h5p_dir}' is not a valid directory or does not exist.")
        return

    # Determine the root directory (parent of the h5p_files folder)
    root_dir = h5p_dir.parent
    # Define the path to the template folder
    template_dir = root_dir / "template"

    # Check if the template folder exists
    if not template_dir.is_dir():
        print(f"Error: Template folder '{template_dir}' not found. "
              "It should be located in the parent directory of your H5P files folder "
              f"(i.e., in '{root_dir}').")
        return

    print(f"Processing H5P files in: {h5p_dir}")
    print(f"Using template from: {template_dir}")
    print(f"Output will be generated in: {root_dir}")
    print("-" * 30)

    # Find all .h5p files directly in the specified folder (non-recursive)
    h5p_files_found = list(h5p_dir.glob("*.h5p"))

    if not h5p_files_found:
        print(f"No .h5p files found directly in '{h5p_dir}'.")
        return

    successful_processing = 0 # Changed variable name here
    for h5p_file_path in h5p_files_found:
        # Get the base name of the H5P file (e.g., "activity1" from "activity1.h5p")
        h5p_base_name = h5p_file_path.stem
        # Define the path for the new output folder (copied template, renamed)
        # This folder will be created in the root_dir
        output_dir = root_dir / h5p_base_name

        print(f"\nProcessing file: {h5p_file_path.name}...")

        try:
            # 1. Create a new folder from the template, named after the H5P file.
            # If the output directory already exists, remove it first to ensure a fresh copy.
            if output_dir.exists():
                print(f"  Output directory '{output_dir}' already exists. Removing it first.")
                shutil.rmtree(output_dir)
            
            print(f"  Copying template '{template_dir}' to '{output_dir}'...")
            shutil.copytree(template_dir, output_dir)

            # 2. Create the 'h5p-folder' inside the newly copied and renamed template folder.
            extraction_target_dir = output_dir / "h5p-folder"
            # parents=True allows creation of parent dirs if needed (though output_dir should exist)
            # exist_ok=True prevents an error if it somehow already exists (shouldn't happen with rmtree above)
            extraction_target_dir.mkdir(parents=True, exist_ok=True) 

            # 3. Extract the content of the .h5p file into the 'h5p-folder'.
            # .h5p files are essentially zip archives.
            print(f"  Extracting '{h5p_file_path.name}' to '{extraction_target_dir}'...")
            with zipfile.ZipFile(h5p_file_path, 'r') as zip_ref:
                zip_ref.extractall(extraction_target_dir)
            
            print(f"  Successfully processed '{h5p_file_path.name}'. Output is in '{output_dir}'.")
            successful_processing += 1 # Changed variable name here

        except FileNotFoundError as e:
            print(f"  Error: A file or directory was not found during processing of '{h5p_file_path.name}': {e}")
        except PermissionError as e:
            print(f"  Error: Permission denied during processing of '{h5p_file_path.name}': {e}")
        except zipfile.BadZipFile:
            print(f"  Error: '{h5p_file_path.name}' is not a valid H5P (zip) file or is corrupted.")
        except Exception as e:
            print(f"  An unexpected error occurred while processing '{h5p_file_path.name}': {e}")
            # Optional: Clean up partially created output_dir if an error occurs mid-process.
            # This can prevent leaving incomplete folders.
            if output_dir.exists():
                try:
                    shutil.rmtree(output_dir)
                    print(f"  Cleaned up partially created directory '{output_dir}'.")
                except Exception as cleanup_e:
                    print(f"  Error during cleanup of '{output_dir}': {cleanup_e}")
    
    print("-" * 30)
    print(f"Finished processing. {successful_processing} of {len(h5p_files_found)} H5P files were processed.") # Changed variable name here


if __name__ == "__main__":
    print("H5P File Processor")
    print("==================")
    print("This script automates the processing of .h5p files based on a template.")
    print("\nExpected folder structure:")
    print("  root_project_folder/")
    print("  ├── your_h5p_files_folder/  <-- Folder containing your .h5p files (e.g., my-activity.h5p)")
    print("  │   └── my-activity.h5p")
    print("  │   └── another-activity.h5p")
    print("  └── template/                 <-- Your template folder (e.g., contains index.html, css/)")
    print("      ├── index.html")
    print("      └── assets/")
    print("\nAfter running, for each .h5p file, you'll get:")
    print("  root_project_folder/")
    print("  ├── your_h5p_files_folder/ ")
    print("  │   └── ... (original .h5p files)")
    print("  ├── template/")
    print("  │   └── ... (original template)")
    print("  ├── my-activity/              <-- Copied 'template', renamed after 'my-activity.h5p'")
    print("  │   ├── index.html            <-- (from template)")
    print("  │   ├── assets/               <-- (from template)")
    print("  │   └── h5p-folder/           <-- Extracted content of 'my-activity.h5p'")
    print("  │       ├── content.json")
    print("  │       └── ... (other H5P assets)")
    print("  └── another-activity/         <-- Copied 'template', renamed after 'another-activity.h5p'")
    print("      └── ... (similar structure)")
    print("=" * 30)

    folder_path = input("Enter the full path to the folder containing your .h5p files: ")
    process_h5p_files(folder_path)
    print("\nScript execution finished.")
