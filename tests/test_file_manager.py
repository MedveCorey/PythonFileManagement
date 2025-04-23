import shutil
import pytest
from pathlib import Path

def test_config_loading(organizer, test_config):
    # Save config to temporary file
    config_file = Path("test_config.json")
    config_file.write_text('{"downloads_dir": "/test"}')
    
    # Test valid config
    config = organizer.load_config(config_file)
    assert config["downloads_dir"] == "/test"
    
    # Test invalid config
    config_file.unlink()
    with pytest.raises(SystemExit):
        organizer.load_config(config_file)

def test_file_organization(organizer, test_config, sample_files):
    # Run organizer
    organizer.run_organizer(test_config)
    
    # Verify file movements
    downloads = Path(test_config["downloads_dir"])
    for filename, category in sample_files:
        target_dir = test_config["target_directories"].get(category)
        if target_dir:
            assert (Path(target_dir) / filename).exists()
            assert not (downloads / filename).exists()
        else:
            assert (downloads / filename).exists()

def test_dry_run(organizer, test_config, sample_files):
    # Run in dry mode
    organizer.run_organizer(test_config, dry_run=True)
    
    # Verify no files moved
    downloads = Path(test_config["downloads_dir"])
    for filename, _ in sample_files:
        assert (downloads / filename).exists()

def test_special_characters(organizer, test_config):
    downloads = Path(test_config["downloads_dir"])
    test_file = downloads / "test file [1].txt"
    test_file.touch()
    
    organizer.run_organizer(test_config)
    target = Path(test_config["target_directories"]["documents"]) / "test file [1].txt"
    assert target.exists()

def test_existing_file_handling(organizer, test_config):
    # Create conflicting files
    downloads = Path(test_config["downloads_dir"])
    target = Path(test_config["target_directories"]["documents"])
    
    (downloads / "test.txt").touch()
    (target / "test.txt").touch()
    
    organizer.run_organizer(test_config)
    assert len(list(target.glob("test*.txt"))) == 2  # Should have duplicate

def test_signal_handling(organizer, test_config):
    # Test SIGINT handling
    import signal
    organizer.running = True
    organizer.signal_handler(signal.SIGINT, None)
    assert organizer.running is False

def test_directory_creation(organizer, test_config):
    # Test missing target directory creation
    target = Path(test_config["target_directories"]["documents"])
    shutil.rmtree(target)
    
    (Path(test_config["downloads_dir"]) / "test.txt").touch()
    organizer.run_organizer(test_config)
    assert target.exists()

def test_permission_handling(organizer, test_config, monkeypatch):
    # Simulate permission error
    def mock_move(*args, **kwargs):
        raise PermissionError("Test error")
    
    monkeypatch.setattr(shutil, "move", mock_move)
    
    (Path(test_config["downloads_dir"]) / "test.txt").touch()
    organizer.run_organizer(test_config)
    
    # Verify error was logged but program continued
    assert (Path(test_config["downloads_dir"]) / "test.txt").exists()

def test_schedule_integration(organizer, test_config):
    # Test scheduled execution
    import schedule
    organizer.config = test_config
    
    # Run scheduled job directly
    schedule.run_all()
    
    # Verify files processed
    downloads = Path(test_config["downloads_dir"])
    assert len(list(downloads.glob("*"))) == 0  # All files moved
