"""Core data models for genex."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional
from datetime import date


class Sex(Enum):
    MALE = "M"
    FEMALE = "F"
    UNKNOWN = "U"


class RiskLevel(Enum):
    NORMAL = "normal"
    CARRIER = "carrier"
    ELEVATED = "elevated"
    HIGH = "high"
    UNKNOWN = "unknown"


class GenomeBuild(Enum):
    GRCH37 = "GRCh37"
    GRCH38 = "GRCh38"
    UNKNOWN = "unknown"


class DataSource(Enum):
    TWENTYTHREE_AND_ME = "23andme"
    ANCESTRY_DNA = "ancestry"
    MYHERITAGE = "myheritage"
    FTDNA = "ftdna"
    VCF = "vcf"
    UNKNOWN = "unknown"


@dataclass
class SNP:
    """A single nucleotide polymorphism."""
    rsid: str
    chromosome: str
    position: int
    genotype: str
    source: DataSource = DataSource.UNKNOWN
    build: GenomeBuild = GenomeBuild.GRCH37

    @property
    def is_called(self) -> bool:
        """Check if SNP has a valid call (not -- or missing)."""
        return self.genotype not in ("--", "", "NC", "II", "DD", None)

    @property
    def alleles(self) -> tuple[str, str]:
        """Split genotype into two alleles."""
        if len(self.genotype) == 2:
            return (self.genotype[0], self.genotype[1])
        return (self.genotype, self.genotype)

    def count_allele(self, allele: str) -> int:
        """Count occurrences of a specific allele."""
        return self.genotype.count(allele)


@dataclass
class SNPAnnotation:
    """Annotation data for a SNP from curated database."""
    rsid: str
    gene: str
    category: str  # health, pharma, trait, carrier
    description: str
    risk_allele: Optional[str] = None
    normal_allele: Optional[str] = None
    condition: Optional[str] = None
    source: str = "genex-curated"
    source_version: str = "1.0.0"
    clinical_significance: Optional[str] = None
    drugs: Optional[str] = None  # For pharma SNPs


@dataclass
class HealthFinding:
    """A health-related finding from genetic analysis."""
    snp: SNP
    annotation: SNPAnnotation
    risk_level: RiskLevel
    interpretation: str
    recommendation: Optional[str] = None

    @property
    def requires_disclaimer(self) -> bool:
        return self.risk_level in (RiskLevel.ELEVATED, RiskLevel.HIGH, RiskLevel.CARRIER)


@dataclass
class AncestrySegment:
    """A chromosomal segment with ancestry assignment."""
    ancestry: str
    chromosome: str
    start: int
    end: int
    copy: int  # 1 or 2 (maternal/paternal)

    @property
    def length(self) -> int:
        return self.end - self.start


@dataclass
class Individual:
    """An individual in a family tree."""
    id: str
    name: str = ""
    given_name: str = ""
    surname: str = ""
    sex: Sex = Sex.UNKNOWN
    birth_date: Optional[str] = None
    birth_place: Optional[str] = None
    death_date: Optional[str] = None
    death_place: Optional[str] = None
    family_child: Optional[str] = None  # Family ID where this person is a child
    families_spouse: list[str] = field(default_factory=list)


@dataclass
class Family:
    """A family unit in a family tree."""
    id: str
    husband_id: Optional[str] = None
    wife_id: Optional[str] = None
    marriage_date: Optional[str] = None
    marriage_place: Optional[str] = None
    children: list[str] = field(default_factory=list)


@dataclass
class GenexConfig:
    """Configuration for genex."""
    data_dir: str
    db_path: str
    network_enabled: bool = False
    encrypted: bool = False
    genome_build: GenomeBuild = GenomeBuild.GRCH37
