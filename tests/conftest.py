import pytest
import shutil
from pathlib import Path
from file_manager import FileOrganizer

@pytest.fixture
def organizer():
    return FileOrganizer()

@pytest.fixture
def test_config(tmp_path):
    downloads = tmp_path / "downloads"
    organized = tmp_path / "organized"

    (downloads).mkdir()
    (organized / "documents").mkdir(parents=True)
    (organized / "images").mkdir(parents=True)
    (organized / "music").mkdir(parents=True)

    return {
        "downloads_dir": str(downloads),
        "target_directories": {
            "documents": str(organized / "documents"),
            "images": str(organized / "images"),
            "music": str(organized / "music")
        },
        "file_types": {
            "documents": [".txt", ".pdf"],
            "images": [".jpg", ".png"],
            "music": [".mp3", ".wav"]
        }
    }

@pytest.fixture
def sample_files(tmp_path):
    downloads = tmp_path / "downloads"
    files = [
        ("test.txt", "documents"),
        ("image.jpg", "images"),
        ("song.mp3", "music"),
        ("unknown.xyz", None)
    ]
    
    for filename, _ in files:
        (downloads / filename).touch()
    
    return files
