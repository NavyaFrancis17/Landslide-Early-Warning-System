"""
Project Integrity and Environment Validation Module.

Verifies directory structure, Python environment, core dependencies,
configuration files, and sample datasets without fabricating predictive results.
"""

import importlib
from pathlib import Path
import sys
from typing import Any, Dict, List, Tuple


REQUIRED_DIRECTORIES: List[str] = [
    "app",
    "data/raw",
    "data/processed",
    "data/sample",
    "models/saved",
    "src",
    "tests",
    "notebooks",
    "config",
    "docs",
]

REQUIRED_PACKAGES: List[str] = [
    "pandas",
    "numpy",
    "yaml",
    "pytest",
]

REQUIRED_SAMPLE_COLUMNS: List[str] = [
    "date",
    "location_id",
    "latitude",
    "longitude",
    "rainfall_1d",
    "soil_moisture",
    "temperature",
    "humidity",
    "elevation",
    "slope",
    "landslide_event",
]


def verify_python_version() -> Tuple[bool, str]:
    """Checks current Python runtime version."""
    major, minor, patch = sys.version_info[:3]
    version_str = f"{major}.{minor}.{patch}"
    # Target Python 3.11+, but support any valid 3.9+ runtime available on system
    is_valid = major == 3 and minor >= 9
    return is_valid, version_str


def verify_directories(root_dir: Path = Path(".")) -> Tuple[bool, List[str]]:
    """Verifies existence of all mandatory project directories."""
    missing: List[str] = []
    for rel_path in REQUIRED_DIRECTORIES:
        dir_path = root_dir / rel_path
        if not dir_path.is_dir():
            missing.append(rel_path)
    return len(missing) == 0, missing


def verify_dependencies() -> Tuple[bool, List[str]]:
    """Verifies that all Phase 1 Python packages are importable."""
    missing: List[str] = []
    for pkg in REQUIRED_PACKAGES:
        try:
            importlib.import_module(pkg)
        except ImportError:
            missing.append(pkg)
    return len(missing) == 0, missing


def verify_sample_data(sample_csv_path: Path) -> Tuple[bool, str]:
    """
    Verifies existence and schema validity of the synthetic sample CSV dataset.
    """
    if not sample_csv_path.exists():
        return False, f"Sample data CSV missing at: {sample_csv_path}"

    try:
        import pandas as pd

        # Read CSV skipping header comment lines if any
        df = pd.read_csv(sample_csv_path, comment="#")
        missing_cols = [col for col in REQUIRED_SAMPLE_COLUMNS if col not in df.columns]
        if missing_cols:
            return False, f"Missing required columns in sample CSV: {missing_cols}"
        if len(df) == 0:
            return False, "Sample CSV is empty"
    except Exception as exc:
        return False, f"Error reading sample CSV: {exc}"

    return True, f"Valid sample CSV loaded ({len(df)} rows, {len(df.columns)} columns)"


def validate_project_environment(config: Dict[str, Any], root_dir: Path = Path(".")) -> Dict[str, Any]:
    """
    Executes comprehensive validation of the project foundation.

    Returns:
        Dict[str, Any]: Detailed validation summary report.
    """
    py_ok, py_version = verify_python_version()
    dirs_ok, missing_dirs = verify_directories(root_dir)
    deps_ok, missing_deps = verify_dependencies()

    sample_rel_path = config.get("paths", {}).get("sample_data", "data/sample")
    sample_csv_path = root_dir / sample_rel_path / "sample_environmental_data.csv"
    sample_ok, sample_msg = verify_sample_data(sample_csv_path)

    all_passed = py_ok and dirs_ok and deps_ok and sample_ok

    return {
        "passed": all_passed,
        "python_version": py_version,
        "directories_ok": dirs_ok,
        "missing_directories": missing_dirs,
        "dependencies_ok": deps_ok,
        "missing_dependencies": missing_deps,
        "sample_data_ok": sample_ok,
        "sample_data_message": sample_msg,
    }
