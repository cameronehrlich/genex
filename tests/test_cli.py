"""Tests for genex CLI commands."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest
from click.testing import CliRunner

from genex.cli import main, DEFAULT_GENEX_DIR, DEFAULT_DB_PATH
from genex.core.database import GenexDatabase


@pytest.fixture
def cli_runner():
    """Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_genex_home(tmp_path: Path):
    """Temporary genex home directory."""
    genex_dir = tmp_path / ".genex"
    genex_dir.mkdir()
    return genex_dir


@pytest.fixture
def mock_db_path(temp_genex_home: Path):
    """Mock the default database path."""
    db_path = temp_genex_home / "genex.db"
    with patch("genex.cli.DEFAULT_DB_PATH", db_path):
        with patch("genex.cli.DEFAULT_GENEX_DIR", temp_genex_home):
            yield db_path


class TestInitCommand:
    """Tests for 'genex init' command."""

    def test_init_with_valid_data(
        self,
        cli_runner: CliRunner,
        mock_db_path: Path,
        synthetic_genome_path: Path,
        synthetic_gedcom_path: Path,
        tmp_path: Path,
    ):
        """Should initialize database with valid data files."""
        # Create a data directory with our synthetic files
        data_dir = tmp_path / "data"
        data_dir.mkdir()

        # Copy synthetic files to data dir
        import shutil
        shutil.copy(synthetic_genome_path, data_dir / "genome.txt")
        shutil.copy(synthetic_gedcom_path, data_dir / "family.ged")

        result = cli_runner.invoke(main, ["init", str(data_dir)])

        assert result.exit_code == 0
        assert "23andMe genome file" in result.output
        assert "GEDCOM family tree" in result.output
        assert mock_db_path.exists()

    def test_init_empty_directory(
        self,
        cli_runner: CliRunner,
        mock_db_path: Path,
        tmp_path: Path,
    ):
        """Should warn when no data files found."""
        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()

        result = cli_runner.invoke(main, ["init", str(empty_dir)])

        assert "No recognized genetic data files found" in result.output

    def test_init_nonexistent_directory(self, cli_runner: CliRunner):
        """Should fail for nonexistent directory."""
        result = cli_runner.invoke(main, ["init", "/nonexistent/path"])

        assert result.exit_code != 0


class TestSnpCommand:
    """Tests for 'genex snp' command."""

    def test_snp_lookup(
        self,
        cli_runner: CliRunner,
        db_with_genome: GenexDatabase,
    ):
        """Should look up a SNP."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_genome.db_path):
            result = cli_runner.invoke(main, ["snp", "rs429358"])

        assert result.exit_code == 0
        assert "rs429358" in result.output
        assert "TT" in result.output

    def test_snp_raw_output(
        self,
        cli_runner: CliRunner,
        db_with_genome: GenexDatabase,
    ):
        """Should output just genotype with --raw flag."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_genome.db_path):
            result = cli_runner.invoke(main, ["snp", "rs429358", "--raw"])

        assert result.exit_code == 0
        assert result.output.strip() == "TT"

    def test_snp_not_found(
        self,
        cli_runner: CliRunner,
        db_with_genome: GenexDatabase,
    ):
        """Should handle missing SNP gracefully."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_genome.db_path):
            result = cli_runner.invoke(main, ["snp", "rs_nonexistent"])

        assert "not found" in result.output.lower()


class TestHealthCommand:
    """Tests for 'genex health' command."""

    def test_health_analysis(
        self,
        cli_runner: CliRunner,
        db_with_genome: GenexDatabase,
    ):
        """Should run health analysis."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_genome.db_path):
            result = cli_runner.invoke(main, ["health"])

        assert result.exit_code == 0
        # Should show APOE status at minimum
        assert "APOE" in result.output or "apoe" in result.output.lower()


class TestTreeCommands:
    """Tests for 'genex tree' commands."""

    def test_tree_summary(
        self,
        cli_runner: CliRunner,
        db_with_gedcom: GenexDatabase,
    ):
        """Should show tree summary."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_gedcom.db_path):
            result = cli_runner.invoke(main, ["tree", "summary"])

        assert result.exit_code == 0
        assert "10" in result.output  # 10 individuals

    def test_tree_search(
        self,
        cli_runner: CliRunner,
        db_with_gedcom: GenexDatabase,
    ):
        """Should search family tree."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_gedcom.db_path):
            result = cli_runner.invoke(main, ["tree", "search", "Alex"])

        assert result.exit_code == 0
        assert "Alex" in result.output

    def test_tree_search_no_results(
        self,
        cli_runner: CliRunner,
        db_with_gedcom: GenexDatabase,
    ):
        """Should handle no search results."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_gedcom.db_path):
            result = cli_runner.invoke(
                main, ["tree", "search", "NonexistentPerson12345"]
            )

        assert "No individuals found" in result.output

    def test_tree_ancestors(
        self,
        cli_runner: CliRunner,
        db_with_gedcom: GenexDatabase,
    ):
        """Should show ancestors."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_gedcom.db_path):
            result = cli_runner.invoke(main, ["tree", "ancestors", "--name", "Alex"])

        assert result.exit_code == 0
        assert "Robert" in result.output  # Father
        assert "Sarah" in result.output  # Mother

    def test_tree_ancestors_with_generations(
        self,
        cli_runner: CliRunner,
        db_with_gedcom: GenexDatabase,
    ):
        """Should respect --generations flag."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_gedcom.db_path):
            result = cli_runner.invoke(
                main, ["tree", "ancestors", "--name", "Alex", "-g", "1"]
            )

        assert result.exit_code == 0
        # Should have parents but maybe not grandparents
        assert "Robert" in result.output or "Sarah" in result.output

    def test_tree_ancestors_heuristic(
        self,
        cli_runner: CliRunner,
        db_with_gedcom: GenexDatabase,
    ):
        """Should use heuristic to find root person when no --name given."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_with_gedcom.db_path):
            result = cli_runner.invoke(main, ["tree", "ancestors"])

        assert result.exit_code == 0
        # Should pick a person and show their ancestors
        assert "Ancestors for:" in result.output

class TestStatusCommand:
    """Tests for 'genex status' command."""

    def test_status_with_data(
        self,
        cli_runner: CliRunner,
        db_fully_loaded: GenexDatabase,
    ):
        """Should show status with loaded data."""
        with patch("genex.cli.DEFAULT_DB_PATH", db_fully_loaded.db_path):
            result = cli_runner.invoke(main, ["status"])

        assert result.exit_code == 0
        assert "SNPs:" in result.output
        assert "30" in result.output  # 30 SNPs
        assert "Individuals:" in result.output
        assert "10" in result.output  # 10 individuals

    def test_status_no_database(
        self,
        cli_runner: CliRunner,
        tmp_path: Path,
    ):
        """Should handle missing database."""
        fake_db_path = tmp_path / "nonexistent.db"
        with patch("genex.cli.DEFAULT_DB_PATH", fake_db_path):
            result = cli_runner.invoke(main, ["status"])

        assert "No genex database found" in result.output


class TestVersionFlag:
    """Tests for version flag."""

    def test_version(self, cli_runner: CliRunner):
        """Should show version."""
        result = cli_runner.invoke(main, ["--version"])

        assert result.exit_code == 0
        assert "0.1.0" in result.output
