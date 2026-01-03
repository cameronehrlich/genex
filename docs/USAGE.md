# Usage Guide

## Getting Your Data

### 23andMe

1. Log into [23andMe](https://www.23andme.com)
2. Go to **Settings** → **23andMe Data** → **Download Your Data**
3. Request your raw data download
4. You'll receive an email when it's ready (usually within 30 minutes)
5. Download and unzip the file

You'll get a text file like `genome_YourName_v5_Full_20240101.txt`.

### GEDCOM (Optional)

If you want to explore your family tree:

1. Export a GEDCOM file from your genealogy software (Ancestry, FamilySearch, Gramps, etc.)
2. Place it in the same directory as your genetic data

## Initialization

Point genex at the directory containing your data:

```bash
genex init ~/Downloads/23andme-data/
```

genex will scan for recognized files:

```
Scanning /Users/you/Downloads/23andme-data/...
  ✓ 23andMe genome file: genome_YourName_v5_Full_20240101.txt
    Loading 640,000 SNPs...
  ✓ GEDCOM family tree: family.ged
    Loading 150 individuals...

Initialized genex database at ~/.genex/genex.db

Summary:
  23andMe genome: 640,000 records
  GEDCOM: 150 records
```

### Re-importing

To replace your data:

```bash
genex init ~/new-data/ --force
```

## Looking Up SNPs

### Single SNP

```bash
genex snp rs429358
```

Output includes:
- Your genotype
- Chromosome and position
- Gene name (if annotated)
- Clinical significance (if known)

### Raw Output

For scripting:

```bash
genex snp rs429358 --raw
# Output: TT
```

### Checking Provenance

```bash
genex snp rs429358 --provenance
```

Shows the source of the annotation (ClinVar, PharmGKB, etc.).

## Health Analysis

```bash
genex health
```

Shows:
- APOE status (Alzheimer's risk factor)
- Cardiovascular variants (Factor V Leiden, etc.)
- Other health-related SNPs in the database

### Filtering by Category

```bash
genex health --category cardiovascular
genex health --category carrier
```

## Pharmacogenomics

```bash
genex pharma
```

Shows how you metabolize common drugs:
- Warfarin sensitivity (VKORC1, CYP2C9)
- Clopidogrel metabolism (CYP2C19)
- Codeine metabolism (CYP2D6)
- Statin risk (SLCO1B1)

## Traits

```bash
genex traits
```

Shows trait-related variants:
- Caffeine metabolism
- Lactose tolerance
- Bitter taste perception
- Muscle fiber type
- And others

## Ancestry

If you imported ancestry composition data:

```bash
genex ancestry
```

Shows chromosome-by-chromosome ancestry breakdown.

## Family Tree

### Overview

```bash
genex tree summary
```

Shows how many individuals are in your tree and identifies a likely "root" person.

### Search

```bash
genex tree search "Smith"
genex tree search "Berlin"
```

Searches names, surnames, and birthplaces.

### Ancestors

```bash
# Ancestors of the auto-detected root person
genex tree ancestors

# Ancestors of a specific person
genex tree ancestors --name "John Smith"

# Limit generations
genex tree ancestors --name "John" -g 3
```

## Status

Check what's loaded:

```bash
genex status
```

Output:

```
genex status
  Database: /Users/you/.genex/genex.db

Data loaded:
  SNPs: 640,000
  Individuals: 150

Sources:
  Genome: genome_YourName_v5_Full_20240101.txt
  Family tree: family.ged
  Annotation DB: v1.0.0
```

## Database Location

genex stores its database at `~/.genex/genex.db`. To start fresh:

```bash
rm -rf ~/.genex
genex init /path/to/data/
```

## Scripting

genex commands can be used in scripts:

```bash
# Get APOE genotypes
rs429358=$(genex snp rs429358 --raw)
rs7412=$(genex snp rs7412 --raw)
echo "APOE: rs429358=$rs429358, rs7412=$rs7412"
```

## Troubleshooting

### "No genex database found"

Run `genex init <directory>` first.

### "SNP not found"

The SNP either:
- Isn't in your 23andMe data (not all rsids are tested)
- Exists but with a different rsid (some SNPs have multiple names)

### "No recognized files found"

genex looks for:
- `.txt` files with "23andMe" in the header
- `.ged` files starting with "0 HEAD"
- `.csv` files with "ancestry" in the filename

Make sure your files aren't still zipped.

### Slow initialization

The first import of a 23andMe file (600k+ SNPs) takes 10-30 seconds. Subsequent commands read from the SQLite database and are fast.
