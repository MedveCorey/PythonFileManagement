import shutil
import schedule
import time
import logging
import json
import signal
import os
import sys
from pathlib import Path
from typing import Dict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')



def load_config(config_path: str) -> Dict:
    """
    Load a JSON configuration file and return its contents as a dictionary.

    Parameters:
    config_path (str): The path to the JSON configuration file.

    Returns:
    Dict: A dictionary containing the configuration settings.

    Raises:
    FileNotFoundError: If the specified configuration file does not exist.
    json.JSONDecodeError: If the configuration file contains invalid JSON.
    """
    with open(config_path, 'r') as f:
        return json.load(f)

def organize_downloads(source_dir: Path, target_dirs: Dict[str, Path], file_types: Dict [str, tuple], dry_run: bool = False) -> None:

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
                            logging.info(f'{"Would move" if dry_run else "Moved"} {file_path.name} to {target_dir}')
                        except FileNotFoundError:
                            logging.error(f"File not found: {file_path}")
                        except PermissionError:
                            logging.error(f"Permission denied: {file_path}")
                        except shutil.Error as e:
                            logging.error(f"Error moving {target_file_path}: {e}")
                            break


def run_organizer(config: Dict, dry_run: bool = False) -> None:
    downloads_dir = Path(config['downloads_dir'])
    target_directories = {k: Path(v) for k, v in config['target_directories'].items()}
    file_types = config['file_types']
    organize_downloads(downloads_dir, target_directories, file_types, dry_run)
    logging.info("File organization completed.")
    
def signal_handler(signum, frame):
    """
    Handle shutdown signals for graceful program termination.

    This function is designed to be used as a signal handler for SIGINT and SIGTERM.
    It logs an info message and exits the program with a status code of 0.

    Parameters:
    signum (int): The signal number received.
    frame (frame): Current stack frame (can be None).

    Returns:
    None: This function does not return as it calls exit(0).
    """
    global running
    running = False
    logging.info("Received shutdown signal. Exiting...")
    exit(0)

def main():
    # Load configuration
    config = load_config('config.json')
    
    # set up signal handlers for graceful shutdown

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Schedule the organizer to run every day
    schedule.every(1).day.do(run_organizer, config=config)
    logging.info("File organizer started. Press Ctrl + C to exit.")

    try:
        running = True
        while running:
            schedule.run_pending()
            time.sleep(1)
    except KeyboardInterrupt:
        logging.info("Keyboard interrupt received. Exiting...")

if __name__ == "__main__":
    main()