# Demo Session

This shows a typical genex session. All data shown is synthetic.

## Setup

```bash
$ pip install genex
...
Successfully installed genex-0.1.0

$ genex --version
genex, version 0.1.0
```

## Import Data

```bash
$ genex init ~/Downloads/23andme-data/

Scanning /Users/demo/Downloads/23andme-data/...
  ✓ 23andMe genome file: genome_Demo_User_v5_Full_20240315.txt
    Loading 638,124 SNPs...
  ✓ GEDCOM family tree: family_tree.ged
    Loading 87 individuals...

Initialized genex database at /Users/demo/.genex/genex.db

Summary:
  23andMe genome: 638,124 records
  GEDCOM: 87 records
```

## Check Status

```bash
$ genex status

genex status
  Database: /Users/demo/.genex/genex.db

Data loaded:
  SNPs: 638,124
  Individuals: 87

Sources:
  Genome: genome_Demo_User_v5_Full_20240315.txt
  Family tree: family_tree.ged
  Annotation DB: v1.0.0
```

## Look Up a SNP

```bash
$ genex snp rs429358

  rs429358 (APOE)
  ─────────────────────────────────
  Your genotype: TT
  Chromosome 19, position 45411941

  This SNP determines APOE epsilon-4 status.
  TT = No epsilon-4 alleles

$ genex snp rs429358 --raw
TT
```

## Health Analysis

```bash
$ genex health

  APOE Status
  ─────────────────────────────────
  Genotype: ε3/ε3

  No epsilon-4 alleles detected. This is the most common
  genotype, associated with average Alzheimer's risk.

  ─────────────────────────────────

  MTHFR C677T (rs1801133)
  Your genotype: AG (heterozygous)
  Mildly reduced enzyme activity. Consider methylfolate.

  Factor V Leiden (rs6025)
  Your genotype: CC (normal)
  No increased clotting risk from this variant.

  ⚠️  This is not medical advice. Consult a healthcare provider
      for clinical interpretation of genetic results.
```

## Pharmacogenomics

```bash
$ genex pharma

  Drug Metabolism Profile
  ─────────────────────────────────

  ┌─────────────┬────────────┬─────────────────────────────┐
  │ Gene        │ Genotype   │ Effect                      │
  ├─────────────┼────────────┼─────────────────────────────┤
  │ CYP2C19     │ *1/*2      │ Intermediate metabolizer    │
  │ CYP2D6      │ *1/*1      │ Normal metabolizer          │
  │ VKORC1      │ CT         │ Intermediate warfarin dose  │
  │ CYP1A2      │ AC         │ Slow caffeine metabolism    │
  └─────────────┴────────────┴─────────────────────────────┘

  ⚠️  Drug dosing decisions require clinical evaluation.
      Share this information with your prescriber.
```

## Traits

```bash
$ genex traits

  Trait Variants
  ─────────────────────────────────

  Caffeine Metabolism (CYP1A2)
  You are a slow metabolizer. Caffeine stays in your system
  longer than average.

  Lactose Tolerance (MCM6)
  You likely tolerate lactose well into adulthood.

  Bitter Taste (TAS2R38)
  You can taste bitter compounds (PTC/PROP taster).
```

## Family Tree

```bash
$ genex tree summary

  Family Tree Summary
  ─────────────────────────────────
  Total individuals: 87
  Root person: Alex Johnson (b. 1985)

$ genex tree search "Smith"

Found 4 matches:
  • Mary Smith (b. 1920) - Chicago, IL
  • Robert Smith (b. 1945) - Chicago, IL
  • Jennifer Smith (b. 1970) - Los Angeles, CA
  • Michael Smith (b. 1995) - San Francisco, CA

$ genex tree ancestors --name "Alex Johnson"

Ancestors for: Alex Johnson

Generation 1 (Parents):
  • David Johnson (b. 1955)
  • Sarah Miller (b. 1958)

Generation 2 (Grandparents):
  • Robert Johnson (b. 1925)
  • Elizabeth Brown (b. 1928)
  • James Miller (b. 1930)
  • Patricia Davis (b. 1932)

Generation 3 (Great-grandparents):
  • William Johnson (b. 1895)
  • Margaret Wilson (b. 1900)
  ...
```

## Scripting Example

```bash
#!/bin/bash
# Check APOE status

rs429358=$(genex snp rs429358 --raw)
rs7412=$(genex snp rs7412 --raw)

echo "APOE genotypes: rs429358=$rs429358, rs7412=$rs7412"

# Determine APOE type
if [[ "$rs429358" == "TT" && "$rs7412" == "CC" ]]; then
    echo "APOE type: ε3/ε3 (most common)"
elif [[ "$rs429358" == "CT" && "$rs7412" == "CC" ]]; then
    echo "APOE type: ε3/ε4 (one risk allele)"
elif [[ "$rs429358" == "CC" && "$rs7412" == "CC" ]]; then
    echo "APOE type: ε4/ε4 (two risk alleles)"
fi
```
