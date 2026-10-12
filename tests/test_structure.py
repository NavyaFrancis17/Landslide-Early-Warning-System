"""
Tests for verifying project directory structure.
"""

from pathlib import Path
from landslide_early_warning.validator import REQUIRED_DIRECTORIES, verify_directories


def test_required_directories_exist():
    """Test that all required Phase 1 project directories exist on disk."""
    root_dir = Path(__file__).resolve().parent.parent
    success, missing = verify_directories(root_dir)
    assert success, f"Missing required project directories: {missing}"


def test_all_expected_files_exist():
    """Test that mandatory Phase 1 root files exist."""
    root_dir = Path(__file__).resolve().parent.parent
    expected_files = [
        "requirements.txt",
        "config.yaml",
        "README.md",
        ".gitignore",
        "main.py",
        "docs/data_dictionary.md",
        "data/sample/sample_environmental_data.csv",
    ]
    for rel_file in expected_files:
        file_path = root_dir / rel_file
        assert file_path.exists(), f"Mandatory file missing: {rel_file}"
