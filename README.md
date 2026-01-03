# genex

Explore your genetic data and family tree from the terminal. Offline. Private. Local.

## Install

```bash
pip install genex
```

Or install from source:

```bash
git clone https://github.com/cameronehrlich/genex.git
cd genex
pip install -e .
```

## Quick Start

```bash
# Point genex at a folder with your data files
genex init ~/Downloads/genetic-data/

# Look up a specific SNP
genex snp rs429358

# Check health-related variants (APOE, MTHFR, etc.)
genex health

# View drug metabolism info
genex pharma

# Explore your family tree
genex tree summary
genex tree ancestors --name "John"
genex tree search "Berlin"
```

## What You Need

1. **Python 3.10+**

2. **Any of these data files** (or both):

   **Genetic data (23andMe)**
   - Log into 23andMe → Settings → Download Your Data
   - Unzip the downloaded file

   **Family tree (GEDCOM)**
   - Export from Ancestry, FamilySearch, MyHeritage, or any genealogy software
   - Standard `.ged` format

Put your files in a folder and run `genex init` on it. genex auto-detects file types.

## Example Output

```
$ genex snp rs429358

  rs429358 (APOE)
  ─────────────────────────────────
  Your genotype: TT
  Chromosome 19, position 45411941

  This SNP determines APOE epsilon-4 status.
  TT = No epsilon-4 alleles (lower Alzheimer's risk)
```

```
$ genex health

  APOE Status: ε3/ε3
  ─────────────────────────────────
  No epsilon-4 alleles detected.
  This is the most common genotype.

  ⚠️  This is not medical advice. Consult a genetic counselor
      or physician for clinical interpretation.
```

## Privacy

- All processing happens on your machine
- No data is uploaded anywhere
- No analytics or telemetry
- Works fully offline after install
- Database stored at `~/.genex/genex.db`

## What's Included

genex bundles ~450 curated SNP annotations covering:

- **Health**: APOE, MTHFR, Factor V Leiden, BRCA markers
- **Pharmacogenomics**: CYP2C19, CYP2D6, VKORC1 (warfarin), etc.
- **Traits**: Caffeine metabolism, lactose tolerance, bitter taste, etc.
- **Carrier status**: Cystic fibrosis, sickle cell, Tay-Sachs, etc.

This is not a complete database. If you need comprehensive clinical analysis, use a proper genetic counseling service.

## Limitations

- **Not medical advice.** Seriously. Don't make health decisions based on this.
- Genetic data: 23andMe format supported (AncestryDNA format planned)
- Family trees: Standard GEDCOM format from any source (Ancestry, FamilySearch, MyHeritage, etc.)
- The SNP database is curated (~450 variants) but not exhaustive

## Commands

| Command | Description |
|---------|-------------|
| `genex init <dir>` | Import data from directory |
| `genex status` | Show what's loaded |
| `genex snp <rsid>` | Look up a specific SNP |
| `genex health` | Health variant analysis |
| `genex pharma` | Drug metabolism profile |
| `genex traits` | Trait variants |
| `genex ancestry` | Ancestry composition (if imported) |
| `genex tree summary` | Family tree overview |
| `genex tree search <name>` | Search family tree |
| `genex tree ancestors` | Show ancestors |

Run `genex --help` or `genex <command> --help` for details.

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Tests use synthetic data only - no real genetic info
```

## License

MIT. See [LICENSE](LICENSE).

## Acknowledgments

SNP annotations compiled from public sources including ClinVar, PharmGKB, and SNPedia.

This project is not affiliated with 23andMe, Ancestry, or any genetic testing company.
