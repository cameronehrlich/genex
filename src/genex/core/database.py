"""Database layer for genex using SQLite."""

import sqlite3
from collections import deque
from pathlib import Path
from typing import Optional, Iterator
from contextlib import contextmanager

from .models import (
    SNP, SNPAnnotation, Individual, Family, AncestrySegment,
    DataSource, GenomeBuild, Sex, RiskLevel
)


class GenexDatabase:
    """SQLite database for storing genetic and genealogical data."""

    def __init__(self, db_path: Path):
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        """Create tables if they don't exist."""
        with self._connect() as conn:
            conn.executescript("""
                -- SNP genotypes
                CREATE TABLE IF NOT EXISTS snps (
                    rsid TEXT PRIMARY KEY,
                    chromosome TEXT,
                    position INTEGER,
                    genotype TEXT,
                    source TEXT,
                    build TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_snps_chr_pos ON snps(chromosome, position);

                -- SNP annotations (curated database)
                CREATE TABLE IF NOT EXISTS annotations (
                    rsid TEXT PRIMARY KEY,
                    gene TEXT,
                    category TEXT,
                    description TEXT,
                    risk_allele TEXT,
                    normal_allele TEXT,
                    condition TEXT,
                    source TEXT,
                    source_version TEXT,
                    clinical_significance TEXT,
                    drugs TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_annotations_category ON annotations(category);
                CREATE INDEX IF NOT EXISTS idx_annotations_gene ON annotations(gene);

                -- Ancestry segments
                CREATE TABLE IF NOT EXISTS ancestry (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ancestry TEXT,
                    chromosome TEXT,
                    start_pos INTEGER,
                    end_pos INTEGER,
                    copy INTEGER
                );
                CREATE INDEX IF NOT EXISTS idx_ancestry_chr ON ancestry(chromosome);

                -- Individuals (GEDCOM)
                CREATE TABLE IF NOT EXISTS individuals (
                    id TEXT PRIMARY KEY,
                    name TEXT,
                    given_name TEXT,
                    surname TEXT,
                    sex TEXT,
                    birth_date TEXT,
                    birth_place TEXT,
                    death_date TEXT,
                    death_place TEXT,
                    family_child TEXT
                );
                CREATE INDEX IF NOT EXISTS idx_individuals_surname ON individuals(surname);

                -- Families (GEDCOM)
                CREATE TABLE IF NOT EXISTS families (
                    id TEXT PRIMARY KEY,
                    husband_id TEXT,
                    wife_id TEXT,
                    marriage_date TEXT,
                    marriage_place TEXT
                );

                -- Family children (many-to-many)
                CREATE TABLE IF NOT EXISTS family_children (
                    family_id TEXT,
                    child_id TEXT,
                    PRIMARY KEY (family_id, child_id)
                );

                -- Individual spouse families (many-to-many)
                CREATE TABLE IF NOT EXISTS individual_spouse_families (
                    individual_id TEXT,
                    family_id TEXT,
                    PRIMARY KEY (individual_id, family_id)
                );

                -- Metadata
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)

    @contextmanager
    def _connect(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _individual_from_row(self, conn: sqlite3.Connection, row: sqlite3.Row) -> Individual:
        """Build an Individual dataclass from a DB row."""
        spouse_rows = conn.execute(
            "SELECT family_id FROM individual_spouse_families WHERE individual_id = ?",
            (row['id'],)
        ).fetchall()
        sex = Sex(row['sex']) if row['sex'] else Sex.UNKNOWN
        return Individual(
            id=row['id'],
            name=row['name'] or '',
            given_name=row['given_name'] or '',
            surname=row['surname'] or '',
            sex=sex,
            birth_date=row['birth_date'],
            birth_place=row['birth_place'],
            death_date=row['death_date'],
            death_place=row['death_place'],
            family_child=row['family_child'],
            families_spouse=[r['family_id'] for r in spouse_rows],
        )

    # -------------------------------------------------------------------------
    # SNP Operations
    # -------------------------------------------------------------------------

    def insert_snp(self, snp: SNP):
        """Insert or replace a single SNP."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO snps (rsid, chromosome, position, genotype, source, build)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (snp.rsid, snp.chromosome, snp.position, snp.genotype,
                  snp.source.value, snp.build.value))

    def insert_snps_batch(self, snps: Iterator[SNP], batch_size: int = 10000):
        """Insert SNPs in batches for performance."""
        with self._connect() as conn:
            batch = []
            for snp in snps:
                batch.append((
                    snp.rsid, snp.chromosome, snp.position, snp.genotype,
                    snp.source.value, snp.build.value
                ))
                if len(batch) >= batch_size:
                    conn.executemany("""
                        INSERT OR REPLACE INTO snps (rsid, chromosome, position, genotype, source, build)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, batch)
                    batch = []
            if batch:
                conn.executemany("""
                    INSERT OR REPLACE INTO snps (rsid, chromosome, position, genotype, source, build)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, batch)

    def get_snp(self, rsid: str) -> Optional[SNP]:
        """Get a SNP by rsid."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM snps WHERE rsid = ?", (rsid,)
            ).fetchone()
            if row:
                return SNP(
                    rsid=row['rsid'],
                    chromosome=row['chromosome'],
                    position=row['position'],
                    genotype=row['genotype'],
                    source=DataSource(row['source']) if row['source'] else DataSource.UNKNOWN,
                    build=GenomeBuild(row['build']) if row['build'] else GenomeBuild.UNKNOWN,
                )
        return None

    def get_snps_by_rsids(self, rsids: list[str]) -> dict[str, SNP]:
        """Get multiple SNPs by rsid list."""
        result = {}
        with self._connect() as conn:
            placeholders = ','.join('?' * len(rsids))
            rows = conn.execute(
                f"SELECT * FROM snps WHERE rsid IN ({placeholders})", rsids
            ).fetchall()
            for row in rows:
                snp = SNP(
                    rsid=row['rsid'],
                    chromosome=row['chromosome'],
                    position=row['position'],
                    genotype=row['genotype'],
                    source=DataSource(row['source']) if row['source'] else DataSource.UNKNOWN,
                    build=GenomeBuild(row['build']) if row['build'] else GenomeBuild.UNKNOWN,
                )
                result[snp.rsid] = snp
        return result

    def count_snps(self) -> int:
        """Count total SNPs in database."""
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM snps").fetchone()
            return row['count'] if row else 0

    # -------------------------------------------------------------------------
    # Annotation Operations
    # -------------------------------------------------------------------------

    def insert_annotation(self, ann: SNPAnnotation):
        """Insert or replace an annotation."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO annotations
                (rsid, gene, category, description, risk_allele, normal_allele,
                 condition, source, source_version, clinical_significance, drugs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ann.rsid, ann.gene, ann.category, ann.description,
                  ann.risk_allele, ann.normal_allele, ann.condition,
                  ann.source, ann.source_version, ann.clinical_significance, ann.drugs))

    def insert_annotations_batch(self, annotations: list[SNPAnnotation]):
        """Insert annotations in batch."""
        with self._connect() as conn:
            conn.executemany("""
                INSERT OR REPLACE INTO annotations
                (rsid, gene, category, description, risk_allele, normal_allele,
                 condition, source, source_version, clinical_significance, drugs)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (a.rsid, a.gene, a.category, a.description,
                 a.risk_allele, a.normal_allele, a.condition,
                 a.source, a.source_version, a.clinical_significance, a.drugs)
                for a in annotations
            ])

    def get_annotation(self, rsid: str) -> Optional[SNPAnnotation]:
        """Get annotation for a SNP."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM annotations WHERE rsid = ?", (rsid,)
            ).fetchone()
            if row:
                return SNPAnnotation(
                    rsid=row['rsid'],
                    gene=row['gene'],
                    category=row['category'],
                    description=row['description'],
                    risk_allele=row['risk_allele'],
                    normal_allele=row['normal_allele'],
                    condition=row['condition'],
                    source=row['source'],
                    source_version=row['source_version'],
                    clinical_significance=row['clinical_significance'],
                    drugs=row['drugs'],
                )
        return None

    def get_annotations_by_category(self, category: str) -> list[SNPAnnotation]:
        """Get all annotations in a category."""
        result = []
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT * FROM annotations WHERE category = ?", (category,)
            ).fetchall()
            for row in rows:
                result.append(SNPAnnotation(
                    rsid=row['rsid'],
                    gene=row['gene'],
                    category=row['category'],
                    description=row['description'],
                    risk_allele=row['risk_allele'],
                    normal_allele=row['normal_allele'],
                    condition=row['condition'],
                    source=row['source'],
                    source_version=row['source_version'],
                    clinical_significance=row['clinical_significance'],
                    drugs=row['drugs'],
                ))
        return result

    # -------------------------------------------------------------------------
    # Ancestry Operations
    # -------------------------------------------------------------------------

    def insert_ancestry_segments(self, segments: Iterator[AncestrySegment]):
        """Insert ancestry segments."""
        with self._connect() as conn:
            # Clear existing
            conn.execute("DELETE FROM ancestry")
            conn.executemany("""
                INSERT INTO ancestry (ancestry, chromosome, start_pos, end_pos, copy)
                VALUES (?, ?, ?, ?, ?)
            """, [
                (s.ancestry, s.chromosome, s.start, s.end, s.copy)
                for s in segments
            ])

    def get_ancestry_summary(self) -> dict[str, dict[str, int]]:
        """Get ancestry summary by copy."""
        result = {'copy1': {}, 'copy2': {}}
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT ancestry, copy, SUM(end_pos - start_pos) as total_length
                FROM ancestry
                GROUP BY ancestry, copy
            """).fetchall()
            for row in rows:
                key = 'copy1' if row['copy'] == 1 else 'copy2'
                result[key][row['ancestry']] = row['total_length']
        return result

    # -------------------------------------------------------------------------
    # Individual/Family Operations
    # -------------------------------------------------------------------------

    def insert_individual(self, ind: Individual):
        """Insert or replace an individual."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO individuals
                (id, name, given_name, surname, sex, birth_date, birth_place,
                 death_date, death_place, family_child)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (ind.id, ind.name, ind.given_name, ind.surname, ind.sex.value,
                  ind.birth_date, ind.birth_place, ind.death_date, ind.death_place,
                  ind.family_child))

            # Insert spouse families
            conn.execute("DELETE FROM individual_spouse_families WHERE individual_id = ?", (ind.id,))
            for fam_id in ind.families_spouse:
                conn.execute("""
                    INSERT OR IGNORE INTO individual_spouse_families (individual_id, family_id)
                    VALUES (?, ?)
                """, (ind.id, fam_id))

    def insert_family(self, fam: Family):
        """Insert or replace a family."""
        with self._connect() as conn:
            conn.execute("""
                INSERT OR REPLACE INTO families
                (id, husband_id, wife_id, marriage_date, marriage_place)
                VALUES (?, ?, ?, ?, ?)
            """, (fam.id, fam.husband_id, fam.wife_id, fam.marriage_date, fam.marriage_place))

            # Insert children
            conn.execute("DELETE FROM family_children WHERE family_id = ?", (fam.id,))
            for child_id in fam.children:
                conn.execute("""
                    INSERT OR IGNORE INTO family_children (family_id, child_id)
                    VALUES (?, ?)
                """, (fam.id, child_id))

    def get_individual(self, ind_id: str) -> Optional[Individual]:
        """Get an individual by ID."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM individuals WHERE id = ?", (ind_id,)
            ).fetchone()
            if row:
                return self._individual_from_row(conn, row)
        return None

    def get_family(self, fam_id: str) -> Optional[Family]:
        """Get a family by ID."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM families WHERE id = ?", (fam_id,)
            ).fetchone()
            if row:
                child_rows = conn.execute(
                    "SELECT child_id FROM family_children WHERE family_id = ?",
                    (fam_id,)
                ).fetchall()
                return Family(
                    id=row['id'],
                    husband_id=row['husband_id'],
                    wife_id=row['wife_id'],
                    marriage_date=row['marriage_date'],
                    marriage_place=row['marriage_place'],
                    children=[r['child_id'] for r in child_rows],
                )
        return None

    def get_parents(self, individual_id: str) -> tuple[Optional[Individual], Optional[Individual]]:
        """Return the parents of an individual."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT family_child FROM individuals WHERE id = ?",
                (individual_id,)
            ).fetchone()
            if not row:
                return (None, None)
            family_id = row['family_child']
            if not family_id:
                return (None, None)
            family_row = conn.execute(
                "SELECT husband_id, wife_id FROM families WHERE id = ?",
                (family_id,)
            ).fetchone()
            if not family_row:
                return (None, None)

            father = mother = None
            if family_row['husband_id']:
                father_row = conn.execute(
                    "SELECT * FROM individuals WHERE id = ?",
                    (family_row['husband_id'],)
                ).fetchone()
                if father_row:
                    father = self._individual_from_row(conn, father_row)
            if family_row['wife_id']:
                mother_row = conn.execute(
                    "SELECT * FROM individuals WHERE id = ?",
                    (family_row['wife_id'],)
                ).fetchone()
                if mother_row:
                    mother = self._individual_from_row(conn, mother_row)
            return (father, mother)

    def get_ancestors(
        self,
        individual_id: str,
        max_generations: int = 10
    ) -> list[tuple[int, Individual]]:
        """Return a list of ancestors grouped by generation."""
        ancestors: list[tuple[int, Individual]] = []
        seen: set[str] = set()

        with self._connect() as conn:
            queue = deque([(individual_id, 0)])
            while queue:
                current_id, generation = queue.popleft()
                if generation >= max_generations:
                    continue

                row = conn.execute(
                    "SELECT family_child FROM individuals WHERE id = ?",
                    (current_id,)
                ).fetchone()
                if not row:
                    continue
                family_id = row['family_child']
                if not family_id:
                    continue

                family_row = conn.execute(
                    "SELECT husband_id, wife_id FROM families WHERE id = ?",
                    (family_id,)
                ).fetchone()
                if not family_row:
                    continue

                for parent_column in ('husband_id', 'wife_id'):
                    parent_id = family_row[parent_column]
                    if not parent_id or parent_id in seen:
                        continue
                    parent_data = conn.execute(
                        "SELECT * FROM individuals WHERE id = ?",
                        (parent_id,)
                    ).fetchone()
                    if not parent_data:
                        continue
                    parent = self._individual_from_row(conn, parent_data)
                    ancestors.append((generation + 1, parent))
                    seen.add(parent_id)
                    queue.append((parent_id, generation + 1))

        return ancestors

    def find_root_individual(self, name_hint: Optional[str] = None) -> Optional[Individual]:
        """Heuristically select a root person for ancestor traversal."""
        if name_hint:
            matches = self.search_individuals(name_hint)
            if matches:
                return matches[0]

        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM individuals
                WHERE COALESCE(name, '') != ''
                ORDER BY
                    CASE WHEN family_child IS NOT NULL THEN 1 ELSE 0 END DESC,
                    CASE WHEN birth_date IS NOT NULL THEN 1 ELSE 0 END DESC,
                    CASE WHEN birth_place IS NOT NULL THEN 1 ELSE 0 END DESC,
                    LENGTH(name) DESC
                LIMIT 1
                """
            ).fetchone()
            if row:
                return self._individual_from_row(conn, row)
        return None

    def count_individuals(self) -> int:
        """Count individuals in database."""
        with self._connect() as conn:
            row = conn.execute("SELECT COUNT(*) as count FROM individuals").fetchone()
            return row['count'] if row else 0

    def search_individuals(self, query: str) -> list[Individual]:
        """Search individuals by name or surname."""
        result = []
        with self._connect() as conn:
            rows = conn.execute("""
                SELECT id FROM individuals
                WHERE name LIKE ? OR surname LIKE ? OR given_name LIKE ?
            """, (f'%{query}%', f'%{query}%', f'%{query}%')).fetchall()
            for row in rows:
                ind = self.get_individual(row['id'])
                if ind:
                    result.append(ind)
        return result

    # -------------------------------------------------------------------------
    # Metadata Operations
    # -------------------------------------------------------------------------

    def set_metadata(self, key: str, value: str):
        """Set a metadata value."""
        with self._connect() as conn:
            conn.execute(
                "INSERT OR REPLACE INTO metadata (key, value) VALUES (?, ?)",
                (key, value)
            )

    def get_metadata(self, key: str) -> Optional[str]:
        """Get a metadata value."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT value FROM metadata WHERE key = ?", (key,)
            ).fetchone()
            return row['value'] if row else None
