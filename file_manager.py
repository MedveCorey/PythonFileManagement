"""
File Manager Script

This script organizes files in the downloads directory into categorized target directories
based on file extensions. It supports scheduled execution and graceful shutdown.
"""

import shutil
import sys
import time
import logging
import json
import signal

from pathlib import Path
from typing import Any, Dict, Tuple

import schedule

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

RUNNING = True

def load_config(config_path: str) -> Dict[str, Any]:
    """
    Load a JSON configuration file and return its contents as a dictionary.

    Parameters:
    config_path (str): The path to the JSON configuration file.

    Returns:
    Dict[str, Any]: A dictionary containing the configuration settings.

    Raises:
    FileNotFoundError: If the specified configuration file does not exist.
    json.JSONDecodeError: If the configuration file contains invalid JSON.
    """
    with open(config_path, 'r') as f:
        return json.load(f)

def organize_downloads(
        source_dir: Path,
        target_dirs: Dict[str, Path],
        file_types: Dict[str, Tuple[str, ...]],
        dry_run: bool = False
) -> None:
    """
    Organize files from the source directory into target directories based on file types.

    Parameters:
    source_dir (Path): The directory to scan for files.
    target_dirs (Dict[str, Path]): Mapping of category names to target directories.
    file_types (Dict[str, Tuple[str, ...]]): Mapping of category names to file extensions.
    dry_run (bool): If True, only log actions without moving files.
    """
    for file_path in source_dir.rglob('*'):
        if file_path.is_file():
            file_extension = file_path.suffix.lower()
            for category, extensions in file_types.items():
                if file_extension in extensions:
                    target_dir = target_dirs.get(category)
                    if target_dir:
                        try:
                            target_file_path = target_dir / file_path.name
                            if not dry_run:
                                shutil.move(str(file_path), str(target_file_path))
                            logging.info(
                                '%s %s to %s',
                                'Would move' if dry_run else 'Moved',
                                file_path.name,
                                target_dir
                            )
                        except FileNotFoundError:
                            logging.error("File not found: %s", file_path)
                        except PermissionError:
                            logging.error("Permission denied: %s", file_path)
                        except shutil.Error as exc:
                            logging.error("Error moving %s: %s", target_file_path, exc)
                    break  # Stop after first matching category



def run_organizer(config: Dict[str, Any], dry_run: bool = False) -> None:
    downloads_dir = Path(config['downloads_dir'])
    target_directories = {k: Path(v) for k, v in config['target_directories'].items()}
    file_types = config['file_types']
    organize_downloads(downloads_dir, target_directories, file_types, dry_run)
    logging.info("File organization completed.")
    
def signal_handler():
    """
    Handle shutdown signals for graceful program termination.

    This function is designed to be used as a signal handler for SIGINT and SIGTERM.
    It logs an info message and exits the program with a status code of 0.

    Returns:
    None: This function does not return as it calls exit(0).
    """
    global RUNNING
    RUNNING = False
    logging.info("Received shutdown signal. Exiting...")
    sys.exit(0)

def main():
    """
    Main entry point for the file manager script.
    """
    config = load_config('config.json')
    
    # set up signal handlers for graceful shutdown

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Schedule the organizer to run every day
    schedule.every(1).day.do(run_organizer, config=config)
    logging.info("File organizer started. Press Ctrl + C to exit.")

    try:
        while RUNNING:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Exiting...")

if __name__ == "__main__":
    main()