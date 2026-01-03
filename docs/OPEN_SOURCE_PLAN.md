# Open Source Preparation Plan

This document outlines steps to prepare genex for public release.

---

## 1. PII Audit & Cleanup

### Files to Exclude (never commit)

These exist in the parent directory and must not be copied into the genex repo:

| File/Directory | Contents | Action |
|----------------|----------|--------|
| `../data/` | Real genome files, GEDCOM with family names | Do not copy |
| `../docs/GENETIC_ANALYSIS_REPORT.md` | Personal health analysis with full name | Do not copy |
| `../analyze_genome.py`, `../analyze_gedcom.py` | May contain hardcoded paths | Do not copy |
| `../CLAUDE.md`, `../AGENTS.md` | Development notes, may have personal context | Do not copy |
| `../*.mcp.json`, `../opencode.json` | Local tool configs | Do not copy |

### Code Review Checklist

- [ ] Search for hardcoded paths containing usernames: `grep -r "cameronehrlich" src/`
- [ ] Search for hardcoded family names: `grep -ri "ehrlich" src/`
- [ ] Review all string literals in `cli.py` and `terminal.py`
- [ ] Check test fixtures contain only synthetic data (already done - tests/fixtures/ is clean)

### Create .gitignore

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
dist/
build/
.eggs/

# Testing
.pytest_cache/
.coverage
htmlcov/

# IDE
.vscode/
.idea/

# genex user data (critical - never commit)
~/.genex/
*.ged
*.23andme.txt
genome_*.txt
genome_*.zip
*ancestry*.csv
*ancestry*.zip

# Local dev
.env
*.local
```

---

## 2. Repository Structure

The genex subdirectory becomes the standalone repo:

```
genex/
├── README.md              # Primary documentation (write fresh)
├── LICENSE                # MIT license text
├── CONTRIBUTING.md        # How to contribute
├── CHANGELOG.md           # Version history
├── pyproject.toml         # Already exists
├── docs/
│   ├── USAGE.md           # Detailed usage guide
│   ├── DATA_FORMATS.md    # Supported file formats
│   └── ADDING_SNPS.md     # How to extend SNP database
├── src/genex/             # Already exists
├── tests/                 # Already exists (with synthetic fixtures)
└── examples/              # Sample workflows
    └── demo_session.md    # Example CLI session
```

### Files to Create

| File | Purpose | Priority |
|------|---------|----------|
| README.md | First thing users see | High |
| LICENSE | Legal protection | High |
| .gitignore | Prevent accidental commits | High |
| CONTRIBUTING.md | Encourage contributions | Medium |
| docs/USAGE.md | Detailed guide | Medium |
| examples/demo_session.md | Show what it does | Medium |
| CHANGELOG.md | Track versions | Low (can start empty) |

---

## 3. README.md Guidelines

The README is the most important file. Avoid AI-generated feel by:

**Do:**
- Start with what problem this solves (one sentence)
- Show a real terminal screenshot or asciinema recording
- Include copy-paste install command
- Show 3-4 example commands with realistic output
- Be honest about limitations
- Link to detailed docs for depth

**Don't:**
- Use phrases like "powerful", "elegant", "seamless"
- Include a features list with 15+ bullet points
- Start with "Welcome to..." or "This project..."
- Over-explain obvious things
- Include badges nobody cares about

### Suggested README Structure

```markdown
# genex

Query your 23andMe data from the terminal. Runs locally, offline, private.

[terminal gif or screenshot here]

## Install

pip install genex

## Quick Start

# Point genex at your downloaded 23andMe data
genex init ~/Downloads/23andme-data/

# Look up a specific SNP
genex snp rs429358

# Check APOE status (Alzheimer's risk factor)
genex health

# Explore your family tree
genex tree ancestors

## What You Need

- Python 3.10+
- Your raw data from 23andMe (Settings → Download Your Data)
- Optional: GEDCOM file for family tree features

## Privacy

All processing happens on your machine. No data is uploaded anywhere.
No analytics. No telemetry. Works fully offline.

## Limitations

- Not medical advice (seriously)
- Only 23andMe format supported currently
- ~450 curated SNPs, not a complete database

## License

MIT
```

---

## 4. User Experience Improvements

### Current Data Import Flow

```bash
genex init <directory>
```

This scans a directory for recognized files. Works but could be clearer.

### Recommended Improvements

1. **Add `genex init --help` with examples:**
   ```
   Examples:
     genex init ~/Downloads/23andme/
     genex init . --force
   ```

2. **Better first-run messaging:**
   - Explain what file types we're looking for
   - Show which files were found/skipped and why
   - Suggest next command to run

3. **Add `genex doctor` command:**
   - Check if database exists
   - Validate data integrity
   - Suggest fixes for common issues

4. **Consider sample data:**
   - Could include a tiny synthetic genome for demo purposes
   - Let users run `genex demo` to see how it works without their own data

### Error Message Audit

Review these scenarios and ensure helpful messages:

- [ ] User runs command before `genex init`
- [ ] Data directory is empty
- [ ] Data directory has unrecognized files
- [ ] Database is corrupted
- [ ] SNP not found in user's data vs not in annotation DB

---

## 5. Code Quality

### Pre-release Checklist

- [x] Tests pass (51 tests, all synthetic data)
- [ ] No hardcoded absolute paths
- [ ] All imports are relative or from installed packages
- [ ] Version number consistent (pyproject.toml, cli.py --version)
- [ ] No debug print statements
- [ ] Type hints on public functions

### Consider Adding

- [ ] `py.typed` marker for type checking
- [ ] GitHub Actions CI workflow
- [ ] Pre-commit hooks config
- [ ] Code formatting (black/ruff)

---

## 6. Legal & Compliance

### License

MIT is already specified in pyproject.toml. Add full LICENSE file:

```
MIT License

Copyright (c) 2026 Cameron Ehrlich

Permission is hereby granted...
```

### Medical Disclaimers

The spec already requires disclaimers on health output. Verify:

- [ ] `genex health` includes disclaimer
- [ ] `genex pharma` includes disclaimer
- [ ] README mentions "not medical advice"
- [ ] No output that could be construed as diagnosis

### Privacy Statement

Consider adding to README or separate PRIVACY.md:

- What data genex accesses (only what you point it at)
- What data genex stores (~/.genex/genex.db)
- What data leaves your machine (nothing, ever)

---

## 7. Launch Checklist

### Before First Commit

1. [ ] Create fresh git repo in genex/ directory
2. [ ] Verify .gitignore is in place
3. [ ] Run `git status` and review every file
4. [ ] Double-check no PII in any file
5. [ ] Run tests one more time

### Before Publishing to GitHub

1. [ ] Choose repo name (genex? genex-cli?)
2. [ ] Write README.md
3. [ ] Add LICENSE file
4. [ ] Tag initial version (v0.1.0)
5. [ ] Consider: private repo first for review?

### Before Publishing to PyPI

1. [ ] Verify package builds: `python -m build`
2. [ ] Test install in fresh venv
3. [ ] Reserve package name on PyPI
4. [ ] Update pyproject.toml with:
   - Project URLs (GitHub, docs)
   - Classifiers
   - Keywords

---

## 8. Post-Launch

### Documentation Site (Optional)

If the project grows, consider:
- GitHub Pages with mkdocs
- ReadTheDocs integration

### Community

- Issue templates (bug report, feature request)
- Discussion forum or Discord
- Contribution guidelines

### Maintenance

- Dependabot for security updates
- Release schedule (if any)
- Deprecation policy

---

## Priority Order

For a minimal viable open-source release:

1. **Must have:**
   - .gitignore (prevent PII accidents)
   - PII audit pass
   - README.md
   - LICENSE

2. **Should have:**
   - CONTRIBUTING.md
   - docs/USAGE.md
   - Better error messages

3. **Nice to have:**
   - CI/CD
   - Demo mode
   - Docs site

---

## Notes

- The test suite uses synthetic data only - safe to publish
- The curated SNP database (snpdb/curated.py) contains no PII
- The spec (GENEX_SPEC.md) is useful but may want editing for public
- Consider whether to credit AI assistance in CONTRIBUTING.md or keep it implicit
