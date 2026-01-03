"""Tests for genex database layer."""

import pytest

from genex.core.database import GenexDatabase
from genex.core.models import SNP, Individual, Family, DataSource, GenomeBuild, Sex


class TestSNPOperations:
    """Tests for SNP database operations."""

    def test_insert_and_get_snp(self, empty_db: GenexDatabase):
        """Should insert and retrieve a SNP."""
        snp = SNP(
            rsid="rs123456",
            chromosome="1",
            position=12345,
            genotype="AG",
            source=DataSource.TWENTYTHREE_AND_ME,
            build=GenomeBuild.GRCH37,
        )
        empty_db.insert_snp(snp)

        retrieved = empty_db.get_snp("rs123456")
        assert retrieved is not None
        assert retrieved.rsid == "rs123456"
        assert retrieved.genotype == "AG"
        assert retrieved.chromosome == "1"
        assert retrieved.position == 12345

    def test_get_nonexistent_snp(self, empty_db: GenexDatabase):
        """Should return None for missing SNP."""
        result = empty_db.get_snp("rs_does_not_exist")
        assert result is None

    def test_count_snps(self, db_with_genome: GenexDatabase):
        """Should count SNPs correctly."""
        count = db_with_genome.count_snps()
        assert count == 30  # Synthetic genome has 30 SNPs

    def test_get_snps_by_rsids(self, db_with_genome: GenexDatabase):
        """Should retrieve multiple SNPs by rsid list."""
        rsids = ["rs429358", "rs7412", "rs1801133"]
        snps = db_with_genome.get_snps_by_rsids(rsids)

        assert len(snps) == 3
        assert "rs429358" in snps
        assert snps["rs429358"].genotype == "TT"


class TestAnnotationOperations:
    """Tests for SNP annotation operations."""

    def test_get_annotation(self, db_with_annotations: GenexDatabase):
        """Should retrieve annotation for known SNP."""
        ann = db_with_annotations.get_annotation("rs429358")
        assert ann is not None
        assert ann.gene == "APOE"

    def test_get_annotations_by_category(self, db_with_annotations: GenexDatabase):
        """Should filter annotations by category."""
        pharma_anns = db_with_annotations.get_annotations_by_category("pharma")
        assert len(pharma_anns) > 0
        assert all(a.category == "pharma" for a in pharma_anns)


class TestIndividualOperations:
    """Tests for GEDCOM individual operations."""

    def test_insert_and_get_individual(self, empty_db: GenexDatabase):
        """Should insert and retrieve an individual."""
        ind = Individual(
            id="@I1@",
            name="Test Person",
            given_name="Test",
            surname="Person",
            sex=Sex.MALE,
            birth_date="1 JAN 1990",
            birth_place="Test City",
        )
        empty_db.insert_individual(ind)

        retrieved = empty_db.get_individual("@I1@")
        assert retrieved is not None
        assert retrieved.name == "Test Person"
        assert retrieved.sex == Sex.MALE

    def test_count_individuals(self, db_with_gedcom: GenexDatabase):
        """Should count individuals correctly."""
        count = db_with_gedcom.count_individuals()
        assert count == 10

    def test_search_individuals_by_name(self, db_with_gedcom: GenexDatabase):
        """Should find individuals by name search."""
        results = db_with_gedcom.search_individuals("Alex")
        assert len(results) >= 1
        assert any("Alex" in r.name for r in results)

    def test_search_individuals_by_surname(self, db_with_gedcom: GenexDatabase):
        """Should find individuals by surname."""
        results = db_with_gedcom.search_individuals("TestPerson")
        assert len(results) >= 1

    def test_search_individuals_no_match(self, db_with_gedcom: GenexDatabase):
        """Should return empty list for no matches."""
        results = db_with_gedcom.search_individuals("NonexistentName12345")
        assert len(results) == 0


class TestFamilyOperations:
    """Tests for GEDCOM family operations."""

    def test_get_family(self, db_with_gedcom: GenexDatabase):
        """Should retrieve family by ID."""
        family = db_with_gedcom.get_family("@F1@")
        assert family is not None
        assert family.husband_id == "@I2@"
        assert family.wife_id == "@I3@"

    def test_get_family_children(self, db_with_gedcom: GenexDatabase):
        """Should include children in family."""
        family = db_with_gedcom.get_family("@F1@")
        assert "@I1@" in family.children  # Alex
        assert "@I10@" in family.children  # Emily


class TestAncestorTraversal:
    """Tests for ancestor traversal functionality."""

    def test_get_parents(self, db_with_gedcom: GenexDatabase):
        """Should return parents of an individual."""
        father, mother = db_with_gedcom.get_parents("@I1@")  # Alex

        assert father is not None
        assert father.given_name == "Robert"

        assert mother is not None
        assert mother.given_name == "Sarah"

    def test_get_parents_no_parents(self, db_with_gedcom: GenexDatabase):
        """Should return None for individuals without parents in tree."""
        # Henry (great-grandfather) has no parents in the tree
        father, mother = db_with_gedcom.get_parents("@I8@")
        assert father is None
        assert mother is None

    def test_get_ancestors(self, db_with_gedcom: GenexDatabase):
        """Should return ancestors grouped by generation."""
        ancestors = db_with_gedcom.get_ancestors("@I1@", max_generations=5)

        # Should have parents (gen 1), grandparents (gen 2), great-grandparents (gen 3)
        assert len(ancestors) > 0

        # Check generation 1 (parents)
        gen1 = [ind for gen, ind in ancestors if gen == 1]
        assert len(gen1) == 2  # Robert and Sarah

        # Check generation 2 (grandparents)
        gen2 = [ind for gen, ind in ancestors if gen == 2]
        assert len(gen2) == 4  # William, Margaret, James, Elizabeth

    def test_get_ancestors_respects_max_generations(
        self, db_with_gedcom: GenexDatabase
    ):
        """Should stop at max_generations limit."""
        # Only get 1 generation (parents)
        ancestors = db_with_gedcom.get_ancestors("@I1@", max_generations=1)

        generations = {gen for gen, _ in ancestors}
        assert max(generations) == 1

    def test_get_ancestors_handles_cycles(self, db_with_gedcom: GenexDatabase):
        """Should not loop infinitely on potential cycles."""
        # This shouldn't hang even with high max_generations
        ancestors = db_with_gedcom.get_ancestors("@I1@", max_generations=100)
        # Should complete without hanging; our tree has max 4 generations
        assert len(ancestors) <= 20

    def test_get_ancestors_nonexistent_individual(self, db_with_gedcom: GenexDatabase):
        """Should return empty list for nonexistent individual."""
        ancestors = db_with_gedcom.get_ancestors("@NONEXISTENT@", max_generations=5)
        assert ancestors == []

    def test_find_root_individual_with_name(self, db_with_gedcom: GenexDatabase):
        """Should find individual by name hint."""
        person = db_with_gedcom.find_root_individual(name_hint="Alex")
        assert person is not None
        assert "Alex" in person.name

    def test_find_root_individual_heuristic(self, db_with_gedcom: GenexDatabase):
        """Should find a reasonable root person without name hint."""
        person = db_with_gedcom.find_root_individual()
        assert person is not None
        # Should pick someone with parents and recent birth
        assert person.family_child is not None


class TestMetadata:
    """Tests for metadata operations."""

    def test_set_and_get_metadata(self, empty_db: GenexDatabase):
        """Should store and retrieve metadata."""
        empty_db.set_metadata("test_key", "test_value")
        value = empty_db.get_metadata("test_key")
        assert value == "test_value"

    def test_get_nonexistent_metadata(self, empty_db: GenexDatabase):
        """Should return None for missing metadata."""
        value = empty_db.get_metadata("nonexistent_key")
        assert value is None
