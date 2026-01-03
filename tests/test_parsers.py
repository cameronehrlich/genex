"""Tests for genex parsers."""

from pathlib import Path

import pytest

from genex.core.parsers.twentythree import (
    detect_23andme,
    parse_23andme_genome,
    count_snps,
)
from genex.core.parsers.gedcom import (
    detect_gedcom,
    parse_gedcom,
    count_individuals,
)
from genex.core.models import DataSource, GenomeBuild


class Test23andMeParser:
    """Tests for 23andMe genome file parsing."""

    def test_detect_23andme_valid(self, synthetic_genome_path: Path):
        """Should detect valid 23andMe file."""
        assert detect_23andme(synthetic_genome_path) is True

    def test_detect_23andme_invalid(self, tmp_path: Path):
        """Should reject non-23andMe file."""
        fake_file = tmp_path / "fake.txt"
        fake_file.write_text("This is not a genetic data file\nJust some random text.\n")
        assert detect_23andme(fake_file) is False

    def test_count_snps(self, synthetic_genome_path: Path):
        """Should count SNPs correctly."""
        count = count_snps(synthetic_genome_path)
        assert count == 30  # We have 30 SNPs in synthetic file

    def test_parse_genome_returns_snps(self, synthetic_genome_path: Path):
        """Should parse SNPs from genome file."""
        snps = list(parse_23andme_genome(synthetic_genome_path))

        assert len(snps) == 30

        # Check first SNP (rs429358 - APOE)
        apoe_snp = next(s for s in snps if s.rsid == "rs429358")
        assert apoe_snp.chromosome == "19"
        assert apoe_snp.position == 45411941
        assert apoe_snp.genotype == "TT"
        assert apoe_snp.source == DataSource.TWENTYTHREE_AND_ME
        assert apoe_snp.build == GenomeBuild.GRCH37

    def test_parse_genome_handles_all_snps(self, synthetic_genome_path: Path):
        """Should parse all expected SNPs."""
        snps = list(parse_23andme_genome(synthetic_genome_path))
        rsids = {s.rsid for s in snps}

        expected_rsids = {
            "rs429358", "rs7412",  # APOE
            "rs1801133", "rs1801131",  # MTHFR
            "rs6025",  # Factor V Leiden
            "rs10490924",  # ARMS2 macular degeneration
            "rs4988235",  # Lactose tolerance
            "rs762551",  # Caffeine metabolism
        }

        for rsid in expected_rsids:
            assert rsid in rsids, f"Missing expected SNP: {rsid}"


class TestGedcomParser:
    """Tests for GEDCOM file parsing."""

    def test_detect_gedcom_valid(self, synthetic_gedcom_path: Path):
        """Should detect valid GEDCOM file."""
        assert detect_gedcom(synthetic_gedcom_path) is True

    def test_detect_gedcom_invalid(self, tmp_path: Path):
        """Should reject non-GEDCOM file."""
        fake_file = tmp_path / "fake.ged"
        fake_file.write_text("This is not a GEDCOM file\n")
        assert detect_gedcom(fake_file) is False

    def test_count_individuals(self, synthetic_gedcom_path: Path):
        """Should count individuals correctly."""
        count = count_individuals(synthetic_gedcom_path)
        assert count == 10  # We have 10 individuals in synthetic file

    def test_parse_gedcom_returns_individuals_and_families(
        self, synthetic_gedcom_path: Path
    ):
        """Should parse individuals and families from GEDCOM."""
        individuals, families = parse_gedcom(synthetic_gedcom_path)

        assert len(individuals) == 10
        assert len(families) == 4

    def test_parse_gedcom_individual_data(self, synthetic_gedcom_path: Path):
        """Should parse individual details correctly."""
        individuals, _ = parse_gedcom(synthetic_gedcom_path)

        # Check Alex TestPerson (the root person)
        alex = individuals.get("@I1@")
        assert alex is not None
        assert alex.name == "Alex TestPerson"  # Parser strips GEDCOM slashes
        assert alex.given_name == "Alex"
        assert alex.surname == "TestPerson"
        assert alex.birth_date == "15 MAR 1990"
        assert alex.birth_place == "Springfield, State"
        assert alex.family_child == "@F1@"

    def test_parse_gedcom_family_relationships(self, synthetic_gedcom_path: Path):
        """Should parse family relationships correctly."""
        individuals, families = parse_gedcom(synthetic_gedcom_path)

        # Check F1 (Alex's parents)
        f1 = families.get("@F1@")
        assert f1 is not None
        assert f1.husband_id == "@I2@"  # Robert
        assert f1.wife_id == "@I3@"  # Sarah
        assert "@I1@" in f1.children  # Alex
        assert "@I10@" in f1.children  # Emily (sibling)

    def test_parse_gedcom_multi_generation(self, synthetic_gedcom_path: Path):
        """Should handle multi-generational relationships."""
        individuals, families = parse_gedcom(synthetic_gedcom_path)

        # Robert's parents
        robert = individuals["@I2@"]
        assert robert.family_child == "@F2@"

        f2 = families["@F2@"]
        assert f2.husband_id == "@I4@"  # William (grandfather)
        assert f2.wife_id == "@I5@"  # Margaret (grandmother)
