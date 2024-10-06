# File Organizer

## Overview
This File Organizer is a python script designed to automatically sort files from a specified directory into designated target directories based on file types. It runs periodically, keeping your file system organized with minimal manual intervention.

## Features
* **Automatic File Organization**: Moves files from downloads directory to specific folders based on file types.
* **Configurable**: Uses a JSON configuration file to set source and target directories.
* **Periodic Execution**: Runs every day to keep downloads folder organized.
* **Dry Run Option**: Test the organization process without actualy moving files.
* **Logging**: Provides informative logs about the file organization process.
* **Graceful Shutdown** Can be safely stopped using keyboard interrupt (Ctl+C).

## Requirements
* Python 3.6 or higher
* Required Python libraries:
    * `schedule`
    * `pathlib`

You can install the required libraries using pip:

    pip install schedule

## Configuration
The script uses a JSON configuration file (`config.json`) to define its beavior. Here's the expected structure:

    {
       "downloads_dir": "/path/to/Ddownloads",
        "target_directories": {
            "documents": "/path/to/documents",
            "images": "/path/to/pictures",
            "music": "/path/to/music",
            "videos": "/path/to/videos"
        },
        "file_types": {
            "documents": [".txt", ".doc", ".docx", ".pdf", ".pptx"],
            "images": [".png", ".jpg", ".jpeg", ".gif"],
            "music": [".mp3", ".wav", ".flac"],
            "videos": [".mp4", ".avi", ".mov"]
        } 
    }

## Usage
 1. Ensure you have Python 3.6 or higher installed.
 2. Install the required libraries:

        pip install schedule

3. Create a `config.json` file in the same directory as the script, using the structure shown above.
4. Run the script:

        python file_organizer.py

The script will start running and organize file every day. To stop the script, press Ctrl + C.

## File Type Categories

The script organizes files into the following categories:
* Documents: .txt, .doc, .docx, .pdf, .pptx
* Images: .png, .jpg, .jpeg, .gif
* Music: .mp3, .wav, .flac
* Videos: .mp4, avi, .mov

## Logging

The script provides logging information about its operations. You'll see log messages in the console indicating which files are being moved and any errors that occur during the process.

## Customization

You can modify the `config.json` to change the source and target directories, or to adjust the file types associated with each category.

## Note
Ensure that the script has the necessary permissions to read from the source directory and write to the target directories