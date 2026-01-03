"""Health variant analysis module."""

from typing import Optional
from dataclasses import dataclass

from ..core.models import SNP, SNPAnnotation, HealthFinding, RiskLevel
from ..core.database import GenexDatabase


@dataclass
class APOEStatus:
    """APOE genotype status."""
    genotype: str  # e.g., "ε3/ε3"
    rs429358: str
    rs7412: str
    risk_level: RiskLevel
    interpretation: str


def determine_apoe_status(db: GenexDatabase) -> APOEStatus:
    """Determine APOE allele status from SNPs."""
    snps = db.get_snps_by_rsids(["rs429358", "rs7412"])

    rs429358 = snps.get("rs429358")
    rs7412 = snps.get("rs7412")

    rs429358_gt = rs429358.genotype if rs429358 else "--"
    rs7412_gt = rs7412.genotype if rs7412 else "--"

    # APOE allele determination:
    # ε2: rs429358=TT, rs7412=TT
    # ε3: rs429358=TT, rs7412=CC
    # ε4: rs429358=CC, rs7412=CC

    if rs429358_gt == "--" or rs7412_gt == "--":
        # Missing data
        if rs429358_gt == "TT":
            return APOEStatus(
                genotype="ε2/ε3 or ε3/ε3 (no ε4)",
                rs429358=rs429358_gt,
                rs7412=rs7412_gt,
                risk_level=RiskLevel.NORMAL,
                interpretation="No ε4 allele detected. Average or lower Alzheimer's risk.",
            )
        return APOEStatus(
            genotype="Unknown",
            rs429358=rs429358_gt,
            rs7412=rs7412_gt,
            risk_level=RiskLevel.UNKNOWN,
            interpretation="Unable to determine - missing SNP data.",
        )

    if rs429358_gt == "TT" and rs7412_gt == "CC":
        return APOEStatus(
            genotype="ε3/ε3",
            rs429358=rs429358_gt,
            rs7412=rs7412_gt,
            risk_level=RiskLevel.NORMAL,
            interpretation="Most common genotype. Average Alzheimer's risk.",
        )
    elif rs429358_gt == "TT" and rs7412_gt == "CT":
        return APOEStatus(
            genotype="ε2/ε3",
            rs429358=rs429358_gt,
            rs7412=rs7412_gt,
            risk_level=RiskLevel.NORMAL,
            interpretation="Protective genotype. Lower than average Alzheimer's risk.",
        )
    elif rs429358_gt == "TT" and rs7412_gt == "TT":
        return APOEStatus(
            genotype="ε2/ε2",
            rs429358=rs429358_gt,
            rs7412=rs7412_gt,
            risk_level=RiskLevel.NORMAL,
            interpretation="Rare protective genotype. Lowest Alzheimer's risk.",
        )
    elif rs429358_gt == "CT" and rs7412_gt == "CC":
        return APOEStatus(
            genotype="ε3/ε4",
            rs429358=rs429358_gt,
            rs7412=rs7412_gt,
            risk_level=RiskLevel.ELEVATED,
            interpretation="One ε4 copy. ~3x increased Alzheimer's risk.",
        )
    elif rs429358_gt == "CC" and rs7412_gt == "CC":
        return APOEStatus(
            genotype="ε4/ε4",
            rs429358=rs429358_gt,
            rs7412=rs7412_gt,
            risk_level=RiskLevel.HIGH,
            interpretation="Two ε4 copies. ~12x increased Alzheimer's risk.",
        )
    elif rs429358_gt == "CT" and rs7412_gt == "CT":
        return APOEStatus(
            genotype="ε2/ε4",
            rs429358=rs429358_gt,
            rs7412=rs7412_gt,
            risk_level=RiskLevel.ELEVATED,
            interpretation="Mixed genotype - one protective, one risk allele.",
        )
    else:
        return APOEStatus(
            genotype=f"Atypical ({rs429358_gt}/{rs7412_gt})",
            rs429358=rs429358_gt,
            rs7412=rs7412_gt,
            risk_level=RiskLevel.UNKNOWN,
            interpretation="Unusual combination, may need verification.",
        )


def analyze_health_snp(snp: SNP, annotation: SNPAnnotation) -> HealthFinding:
    """Analyze a single health SNP and return a finding."""
    risk_allele = annotation.risk_allele
    genotype = snp.genotype

    # Determine risk level
    if risk_allele and snp.is_called:
        risk_count = genotype.count(risk_allele)
        if risk_count == 2:
            risk_level = RiskLevel.HIGH
            interpretation = f"Homozygous for risk allele ({genotype})"
        elif risk_count == 1:
            risk_level = RiskLevel.CARRIER
            interpretation = f"Heterozygous carrier ({genotype})"
        else:
            risk_level = RiskLevel.NORMAL
            interpretation = f"Normal genotype ({genotype})"
    else:
        risk_level = RiskLevel.UNKNOWN
        interpretation = f"Genotype: {genotype}"

    # Add condition-specific context
    if annotation.condition:
        interpretation += f" for {annotation.condition}"

    return HealthFinding(
        snp=snp,
        annotation=annotation,
        risk_level=risk_level,
        interpretation=interpretation,
        recommendation=_get_recommendation(annotation, risk_level),
    )


def _get_recommendation(annotation: SNPAnnotation, risk_level: RiskLevel) -> Optional[str]:
    """Get recommendation based on finding."""
    if risk_level == RiskLevel.NORMAL:
        return None

    recommendations = {
        "Factor V Leiden Thrombophilia": "Discuss with doctor before surgery or long flights. Avoid hormonal birth control.",
        "Hereditary Hemochromatosis": "Consider iron studies blood test. Avoid iron supplements.",
        "Age-related Macular Degeneration": "Regular comprehensive eye exams. Consider AREDS2 vitamins.",
        "MTHFR Deficiency": "Consider methylfolate instead of folic acid in supplements.",
        "Hereditary Breast and Ovarian Cancer": "Discuss comprehensive BRCA testing with genetic counselor.",
    }

    return recommendations.get(annotation.condition)


def run_health_analysis(db: GenexDatabase) -> list[HealthFinding]:
    """Run comprehensive health variant analysis."""
    findings = []

    # Get all health annotations
    annotations = db.get_annotations_by_category("health")
    rsids = [a.rsid for a in annotations]
    snps = db.get_snps_by_rsids(rsids)

    for annotation in annotations:
        snp = snps.get(annotation.rsid)
        if snp and snp.is_called:
            finding = analyze_health_snp(snp, annotation)
            findings.append(finding)

    return findings
