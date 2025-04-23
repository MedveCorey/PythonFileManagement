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
from typing import Any, Dict, Tuple, Optional

# Ensure package is installed: pip install schedule
import schedule  # Now properly managed via requirements.txt

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


class FileOrganizer:
    """Main class to handle file organization and scheduling"""

    def __init__(self) -> None:
        self.running = True
        self.config: Optional[Dict[str, Any]] = None

    def load_config(self, config_path: str) -> Dict[str, Any]:
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
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logging.error("Config error: %s", str(e))
            sys.exit(1)

    def organize_downloads(
            self,
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
        moved_files = 0
        for file_path in source_dir.rglob('*'):
            if not self.running:
                break

            if file_path.is_file():
                self._process_file(file_path, target_dirs, file_types, dry_run)
                moved_files += 1

        logging.info("Processed %d files", moved_files)

    def _process_file(
            self,
            file_path: Path,
            target_dirs: Dict[str, Path],
            file_types: Dict[str, Tuple[str, ...]],
            dry_run: bool
    ) -> None:
        """Helper method to process individual files"""
        file_extension = file_path.suffix.lower()
        for category, extensions in file_types.items():
            if file_extension in extensions:
                self._move_file(file_path, category, target_dirs, dry_run)
                break

    def _move_file(
            self,
            file_path: Path,
            category: str,
            target_dirs: Dict[str, Path],
            dry_run: bool
    ) -> None:
        """Helper method to handle file movement"""
        target_dir = target_dirs.get(category)
        if not target_dir:
            return

        target_file_path = target_dir / file_path.name
        try:
            if not dry_run:
                shutil.move(str(file_path), str(target_file_path))
            logging.info(
                '%s %s to %s',
                'Would move' if dry_run else 'Moved',
                file_path.name,
                target_dir
            )
        except (FileNotFoundError, PermissionError, shutil.Error) as e:
            logging.error("Error processing %s: %s", file_path.name, str(e))

    def run_organizer(self, config: Dict[str, Any], dry_run: bool = False) -> None:
        """Execute the file organization process"""
        downloads_dir = Path(config['downloads_dir'])
        target_dirs = {k: Path(v) for k, v in config['target_directories'].items()}
        file_types = config['file_types']
        self.organize_downloads(downloads_dir, target_dirs, file_types, dry_run)

    def signal_handler(self, signum: int) -> None:
        """Handle shutdown signals for graceful termination"""
        logging.info("Received shutdown signal (SIG%s). Exiting...",
                   signal.Signals(signum).name)
        self.running = False
        sys.exit(0)

    def main(self) -> None:
        """Main entry point for the file manager script"""
        self.config = self.load_config('config.json')

        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)

        # Schedule organization
        schedule.every(1).day.do(self.run_organizer, config=self.config)
        logging.info("File organizer started. Press Ctrl+C to exit.")

        try:
            while self.running:
                schedule.run_pending()
                time.sleep(1)
        except (KeyboardInterrupt, SystemExit):
            logging.info("Shutdown initiated")
        except Exception as e:  # pylint: disable=broad-exception-caught
            logging.error("Unexpected error: %s", str(e))
            sys.exit(1)
        finally:
            logging.info("File organizer shutdown complete")


if __name__ == "__main__":
    organizer = FileOrganizer()
    organizer.main()
