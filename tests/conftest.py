"""Pytest configuration and fixtures for genex tests."""

import tempfile
from pathlib import Path

import pytest

from genex.core.database import GenexDatabase
from genex.core.parsers.twentythree import parse_23andme_genome
from genex.core.parsers.gedcom import parse_gedcom
from genex.snpdb.curated import get_all_annotations


FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def synthetic_genome_path() -> Path:
    """Path to synthetic 23andMe genome file."""
    return FIXTURES_DIR / "synthetic_genome.txt"


@pytest.fixture
def synthetic_gedcom_path() -> Path:
    """Path to synthetic GEDCOM file."""
    return FIXTURES_DIR / "synthetic_family.ged"


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Temporary database path for testing."""
    return tmp_path / "test_genex.db"


@pytest.fixture
def empty_db(temp_db_path: Path) -> GenexDatabase:
    """Empty database instance."""
    return GenexDatabase(temp_db_path)


@pytest.fixture
def db_with_annotations(temp_db_path: Path) -> GenexDatabase:
    """Database pre-loaded with SNP annotations."""
    db = GenexDatabase(temp_db_path)
    annotations = get_all_annotations()
    db.insert_annotations_batch(annotations)
    return db


@pytest.fixture
def db_with_genome(temp_db_path: Path, synthetic_genome_path: Path) -> GenexDatabase:
    """Database pre-loaded with synthetic genome data."""
    db = GenexDatabase(temp_db_path)

    # Load annotations
    annotations = get_all_annotations()
    db.insert_annotations_batch(annotations)

    # Load genome
    snps = parse_23andme_genome(synthetic_genome_path)
    db.insert_snps_batch(snps)

    return db


@pytest.fixture
def db_with_gedcom(temp_db_path: Path, synthetic_gedcom_path: Path) -> GenexDatabase:
    """Database pre-loaded with synthetic GEDCOM data."""
    db = GenexDatabase(temp_db_path)

    individuals, families = parse_gedcom(synthetic_gedcom_path)
    for ind in individuals.values():
        db.insert_individual(ind)
    for fam in families.values():
        db.insert_family(fam)

    return db


@pytest.fixture
def db_fully_loaded(
    temp_db_path: Path,
    synthetic_genome_path: Path,
    synthetic_gedcom_path: Path
) -> GenexDatabase:
    """Database with all synthetic data loaded."""
    db = GenexDatabase(temp_db_path)

    # Load annotations
    annotations = get_all_annotations()
    db.insert_annotations_batch(annotations)

    # Load genome
    snps = parse_23andme_genome(synthetic_genome_path)
    db.insert_snps_batch(snps)

    # Load GEDCOM
    individuals, families = parse_gedcom(synthetic_gedcom_path)
    for ind in individuals.values():
        db.insert_individual(ind)
    for fam in families.values():
        db.insert_family(fam)

    return db
