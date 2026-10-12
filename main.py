"""
Main Entrypoint for AI-Based Location-Adaptive Landslide Early-Warning System.

Phase 1 — Project Foundation Initializer.
"""

import sys
from pathlib import Path

# Add src directory to module search path for clean import behavior
sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from landslide_early_warning.config_loader import load_config
from landslide_early_warning.validator import validate_project_environment


def main() -> int:
    """
    Initializes Phase 1 project foundation and verifies system environment.
    """
    root_dir = Path(__file__).resolve().parent

    try:
        config = load_config(root_dir / "config.yaml")
    except Exception as exc:
        print(f"Initialization Failure: Unable to load configuration: {exc}")
        return 1

    project_name = config.get("project", {}).get(
        "name", "AI-Based Location-Adaptive Landslide Early-Warning System"
    )
    phase_num = config.get("project", {}).get("phase", 1)

    print("Project:")
    print(f"{project_name}\n")
    print("Phase:")
    print(f"{phase_num} - Project Foundation\n")

    report = validate_project_environment(config, root_dir=root_dir)

    if report["passed"]:
        print("Status:")
        print("Project environment initialized successfully.")
        return 0
    else:
        print("Status:")
        print("Project environment initialization incomplete.")
        if report["missing_directories"]:
            print(f"  Missing Directories: {report['missing_directories']}")
        if report["missing_dependencies"]:
            print(f"  Missing Dependencies: {report['missing_dependencies']}")
        if not report["sample_data_ok"]:
            print(f"  Sample Data Issue: {report['sample_data_message']}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
