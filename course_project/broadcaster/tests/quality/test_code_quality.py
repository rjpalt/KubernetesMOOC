"""Automated code quality validation tests."""

import subprocess
from pathlib import Path

import pytest


class TestCodeQuality:
    """Test code quality standards."""

    def test_ruff_linting_passes(self):
        """Test that ruff linting passes."""
        result = subprocess.run(
            ["uv", "run", "ruff", "check", "src/", "tests/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        assert result.returncode == 0, f"Ruff linting failed:\n{result.stdout}\n{result.stderr}"

    def test_ruff_formatting_check(self):
        """Test that code formatting is correct."""
        result = subprocess.run(
            ["uv", "run", "ruff", "format", "--check", "src/", "tests/"],
            capture_output=True,
            text=True,
            cwd=Path(__file__).parent.parent.parent,
        )
        assert result.returncode == 0, f"Code formatting check failed:\n{result.stdout}\n{result.stderr}"

    def test_import_structure(self):
        """Test that all modules can be imported successfully."""
        try:
            from src.config.settings import settings
            from src.main import app
            from src.services.broadcaster_service import BroadcasterService

            assert app is not None
            assert BroadcasterService is not None
            assert settings is not None
        except ImportError as e:
            pytest.fail(f"Import error: {e}")

    def test_build_scripts_executable(self):
        """Test that all build scripts exist and are executable."""
        project_root = Path(__file__).parent.parent.parent

        scripts = ["build.sh", "build-and-push.sh", "quality.sh", "dev-setup.sh"]
        for script in scripts:
            script_path = project_root / script
            assert script_path.exists(), f"Script {script} not found"
            assert script_path.stat().st_mode & 0o111, f"Script {script} not executable"
