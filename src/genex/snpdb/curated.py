"""Curated SNP annotation database for genex."""

from ..core.models import SNPAnnotation

# Version info
SNPDB_VERSION = "1.0.0"
SNPDB_DATE = "2026-01-02"


def get_all_annotations() -> list[SNPAnnotation]:
    """Get all curated SNP annotations."""
    return (
        get_apoe_annotations() +
        get_health_annotations() +
        get_carrier_annotations() +
        get_pharma_annotations() +
        get_trait_annotations()
    )


def get_apoe_annotations() -> list[SNPAnnotation]:
    """APOE gene annotations for Alzheimer's risk."""
    return [
        SNPAnnotation(
            rsid="rs429358",
            gene="APOE",
            category="health",
            description="APOE epsilon-4 determining SNP",
            risk_allele="C",
            normal_allele="T",
            condition="Alzheimer's Disease Risk",
            clinical_significance="risk factor",
        ),
        SNPAnnotation(
            rsid="rs7412",
            gene="APOE",
            category="health",
            description="APOE epsilon-2 determining SNP",
            risk_allele="T",  # Note: epsilon-2 is protective
            normal_allele="C",
            condition="Alzheimer's Disease Risk",
            clinical_significance="protective factor",
        ),
    ]


def get_health_annotations() -> list[SNPAnnotation]:
    """Health-related SNP annotations."""
    return [
        # Factor V Leiden
        SNPAnnotation(
            rsid="rs6025",
            gene="F5",
            category="health",
            description="Factor V Leiden - blood clotting disorder",
            risk_allele="A",
            normal_allele="G",
            condition="Factor V Leiden Thrombophilia",
            clinical_significance="pathogenic",
        ),
        # Prothrombin
        SNPAnnotation(
            rsid="rs1799963",
            gene="F2",
            category="health",
            description="Prothrombin G20210A mutation",
            risk_allele="A",
            normal_allele="G",
            condition="Prothrombin Thrombophilia",
            clinical_significance="pathogenic",
        ),
        # Hemochromatosis
        SNPAnnotation(
            rsid="rs1800562",
            gene="HFE",
            category="health",
            description="HFE C282Y mutation - iron overload",
            risk_allele="A",
            normal_allele="G",
            condition="Hereditary Hemochromatosis",
            clinical_significance="pathogenic",
        ),
        SNPAnnotation(
            rsid="rs1799945",
            gene="HFE",
            category="health",
            description="HFE H63D mutation - mild iron overload",
            risk_allele="G",
            normal_allele="C",
            condition="Hereditary Hemochromatosis",
            clinical_significance="risk factor",
        ),
        # Macular Degeneration
        SNPAnnotation(
            rsid="rs1061170",
            gene="CFH",
            category="health",
            description="CFH Y402H - major AMD risk factor",
            risk_allele="C",
            normal_allele="T",
            condition="Age-related Macular Degeneration",
            clinical_significance="risk factor",
        ),
        SNPAnnotation(
            rsid="rs10490924",
            gene="ARMS2",
            category="health",
            description="ARMS2/HTRA1 - second major AMD risk factor",
            risk_allele="T",
            normal_allele="G",
            condition="Age-related Macular Degeneration",
            clinical_significance="risk factor",
        ),
        # Celiac
        SNPAnnotation(
            rsid="rs2187668",
            gene="HLA-DQ2.5",
            category="health",
            description="HLA-DQA1*05 tag SNP for celiac susceptibility",
            risk_allele="T",
            normal_allele="C",
            condition="Celiac Disease",
            clinical_significance="risk factor",
        ),
        # MTHFR
        SNPAnnotation(
            rsid="rs1801133",
            gene="MTHFR",
            category="health",
            description="MTHFR C677T - reduced folate metabolism",
            risk_allele="A",
            normal_allele="G",
            condition="MTHFR Deficiency",
            clinical_significance="risk factor",
        ),
        SNPAnnotation(
            rsid="rs1801131",
            gene="MTHFR",
            category="health",
            description="MTHFR A1298C - mild folate metabolism reduction",
            risk_allele="G",
            normal_allele="T",
            condition="MTHFR Deficiency",
            clinical_significance="risk factor",
        ),
        # BRCA (limited - 23andMe only tests a few)
        SNPAnnotation(
            rsid="rs80357906",
            gene="BRCA1",
            category="health",
            description="BRCA1 185delAG Ashkenazi founder mutation",
            risk_allele="D",
            normal_allele="I",
            condition="Hereditary Breast and Ovarian Cancer",
            clinical_significance="pathogenic",
        ),
        SNPAnnotation(
            rsid="rs80357713",
            gene="BRCA1",
            category="health",
            description="BRCA1 5382insC Ashkenazi founder mutation",
            risk_allele="I",
            normal_allele="D",
            condition="Hereditary Breast and Ovarian Cancer",
            clinical_significance="pathogenic",
        ),
        SNPAnnotation(
            rsid="rs80359550",
            gene="BRCA2",
            category="health",
            description="BRCA2 6174delT Ashkenazi founder mutation",
            risk_allele="D",
            normal_allele="I",
            condition="Hereditary Breast and Ovarian Cancer",
            clinical_significance="pathogenic",
        ),
    ]


def get_carrier_annotations() -> list[SNPAnnotation]:
    """Ashkenazi Jewish carrier panel annotations."""
    return [
        # Tay-Sachs
        SNPAnnotation(
            rsid="i4000408",
            gene="HEXA",
            category="carrier",
            description="Tay-Sachs disease carrier marker",
            condition="Tay-Sachs Disease",
            clinical_significance="carrier",
        ),
        # Gaucher
        SNPAnnotation(
            rsid="rs76763715",
            gene="GBA",
            category="carrier",
            description="Gaucher disease N370S mutation",
            risk_allele="A",
            normal_allele="G",
            condition="Gaucher Disease",
            clinical_significance="carrier",
        ),
        # Cystic Fibrosis
        SNPAnnotation(
            rsid="rs113993960",
            gene="CFTR",
            category="carrier",
            description="CFTR F508del - most common CF mutation",
            condition="Cystic Fibrosis",
            clinical_significance="carrier",
        ),
        SNPAnnotation(
            rsid="rs75527207",
            gene="CFTR",
            category="carrier",
            description="CFTR W1282X - common in Ashkenazi",
            condition="Cystic Fibrosis",
            clinical_significance="carrier",
        ),
        # Familial Dysautonomia
        SNPAnnotation(
            rsid="rs111033559",
            gene="IKBKAP",
            category="carrier",
            description="Familial Dysautonomia IVS20+6T>C",
            condition="Familial Dysautonomia",
            clinical_significance="carrier",
        ),
        # Canavan
        SNPAnnotation(
            rsid="rs12946976",
            gene="ASPA",
            category="carrier",
            description="Canavan disease E285A mutation",
            condition="Canavan Disease",
            clinical_significance="carrier",
        ),
        # Bloom Syndrome
        SNPAnnotation(
            rsid="rs113993959",
            gene="BLM",
            category="carrier",
            description="Bloom syndrome blmAsh mutation",
            condition="Bloom Syndrome",
            clinical_significance="carrier",
        ),
    ]


def get_pharma_annotations() -> list[SNPAnnotation]:
    """Pharmacogenomic annotations."""
    return [
        # CYP2C19
        SNPAnnotation(
            rsid="rs4244285",
            gene="CYP2C19",
            category="pharma",
            description="CYP2C19*2 - poor metabolizer allele",
            risk_allele="A",
            normal_allele="G",
            drugs="clopidogrel, omeprazole, citalopram, escitalopram",
            clinical_significance="poor metabolizer",
        ),
        SNPAnnotation(
            rsid="rs4986893",
            gene="CYP2C19",
            category="pharma",
            description="CYP2C19*3 - poor metabolizer allele",
            risk_allele="A",
            normal_allele="G",
            drugs="clopidogrel, PPIs",
            clinical_significance="poor metabolizer",
        ),
        SNPAnnotation(
            rsid="rs12248560",
            gene="CYP2C19",
            category="pharma",
            description="CYP2C19*17 - ultra-rapid metabolizer allele",
            risk_allele="T",
            normal_allele="C",
            drugs="clopidogrel (increased effect), escitalopram",
            clinical_significance="ultra-rapid metabolizer",
        ),
        # CYP2D6
        SNPAnnotation(
            rsid="rs3892097",
            gene="CYP2D6",
            category="pharma",
            description="CYP2D6*4 - poor metabolizer allele",
            risk_allele="A",
            normal_allele="G",
            drugs="codeine, tramadol, tamoxifen, antidepressants",
            clinical_significance="poor metabolizer",
        ),
        SNPAnnotation(
            rsid="rs16947",
            gene="CYP2D6",
            category="pharma",
            description="CYP2D6*2 allele marker",
            drugs="various",
        ),
        # SLCO1B1 - Statins
        SNPAnnotation(
            rsid="rs4149056",
            gene="SLCO1B1",
            category="pharma",
            description="SLCO1B1*5 - statin myopathy risk",
            risk_allele="C",
            normal_allele="T",
            drugs="simvastatin, atorvastatin, rosuvastatin",
            clinical_significance="increased toxicity risk",
        ),
        # Warfarin
        SNPAnnotation(
            rsid="rs9923231",
            gene="VKORC1",
            category="pharma",
            description="VKORC1 -1639G>A - warfarin sensitivity",
            risk_allele="T",
            normal_allele="C",
            drugs="warfarin",
            clinical_significance="increased sensitivity",
        ),
        SNPAnnotation(
            rsid="rs1799853",
            gene="CYP2C9",
            category="pharma",
            description="CYP2C9*2 - warfarin sensitivity",
            risk_allele="T",
            normal_allele="C",
            drugs="warfarin, NSAIDs, phenytoin",
            clinical_significance="poor metabolizer",
        ),
        SNPAnnotation(
            rsid="rs1057910",
            gene="CYP2C9",
            category="pharma",
            description="CYP2C9*3 - warfarin sensitivity",
            risk_allele="C",
            normal_allele="A",
            drugs="warfarin, NSAIDs, phenytoin",
            clinical_significance="poor metabolizer",
        ),
        # DPYD - Fluorouracil
        SNPAnnotation(
            rsid="rs3918290",
            gene="DPYD",
            category="pharma",
            description="DPYD*2A - severe 5-FU toxicity risk",
            risk_allele="A",
            normal_allele="G",
            drugs="5-fluorouracil, capecitabine",
            clinical_significance="increased toxicity risk",
        ),
        # CYP3A5
        SNPAnnotation(
            rsid="rs776746",
            gene="CYP3A5",
            category="pharma",
            description="CYP3A5*3 - non-expressor allele",
            drugs="tacrolimus, cyclosporine, some statins",
        ),
    ]


def get_trait_annotations() -> list[SNPAnnotation]:
    """Trait and wellness annotations."""
    return [
        # Caffeine
        SNPAnnotation(
            rsid="rs762551",
            gene="CYP1A2",
            category="trait",
            description="Caffeine metabolism speed",
            risk_allele="C",
            normal_allele="A",
            condition="Caffeine Metabolism",
        ),
        # Lactose
        SNPAnnotation(
            rsid="rs4988235",
            gene="MCM6",
            category="trait",
            description="Lactase persistence (lactose tolerance)",
            risk_allele="C",
            normal_allele="T",
            condition="Lactose Intolerance",
        ),
        # Alcohol flush
        SNPAnnotation(
            rsid="rs671",
            gene="ALDH2",
            category="trait",
            description="Alcohol flush reaction",
            risk_allele="A",
            normal_allele="G",
            condition="Alcohol Flush Reaction",
        ),
        # Muscle type
        SNPAnnotation(
            rsid="rs1815739",
            gene="ACTN3",
            category="trait",
            description="Muscle fiber composition (R577X)",
            risk_allele="T",
            normal_allele="C",
            condition="Muscle Fiber Type",
        ),
        # Bitter taste
        SNPAnnotation(
            rsid="rs713598",
            gene="TAS2R38",
            category="trait",
            description="Bitter taste perception (PTC/PROP)",
            condition="Bitter Taste Perception",
        ),
        SNPAnnotation(
            rsid="rs1726866",
            gene="TAS2R38",
            category="trait",
            description="Bitter taste perception",
            condition="Bitter Taste Perception",
        ),
        SNPAnnotation(
            rsid="rs10246939",
            gene="TAS2R38",
            category="trait",
            description="Bitter taste perception",
            condition="Bitter Taste Perception",
        ),
        # Cilantro
        SNPAnnotation(
            rsid="rs72921001",
            gene="OR6A2",
            category="trait",
            description="Cilantro taste perception",
            risk_allele="A",
            normal_allele="C",
            condition="Cilantro Aversion",
        ),
        # Eye color
        SNPAnnotation(
            rsid="rs12913832",
            gene="HERC2",
            category="trait",
            description="Eye color determination",
            condition="Eye Color",
        ),
        # Earwax
        SNPAnnotation(
            rsid="rs17822931",
            gene="ABCC11",
            category="trait",
            description="Earwax type (wet vs dry)",
            condition="Earwax Type",
        ),
        # Asparagus smell
        SNPAnnotation(
            rsid="rs4481887",
            gene="OR2M7",
            category="trait",
            description="Asparagus metabolite smell detection",
            condition="Asparagus Anosmia",
        ),
        # Vitamin D
        SNPAnnotation(
            rsid="rs2282679",
            gene="GC",
            category="trait",
            description="Vitamin D binding protein levels",
            condition="Vitamin D Levels",
        ),
        SNPAnnotation(
            rsid="rs10741657",
            gene="CYP2R1",
            category="trait",
            description="Vitamin D metabolism",
            condition="Vitamin D Levels",
        ),
    ]
