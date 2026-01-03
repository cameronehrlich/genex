# Contributing to genex

Thanks for your interest in contributing.

## Development Setup

```bash
git clone https://github.com/cameronehrlich/genex.git
cd genex
pip install -e ".[dev]"
pytest
```

## Running Tests

```bash
# All tests
pytest

# Specific test file
pytest tests/test_cli.py

# With coverage
pytest --cov=genex
```

Tests use synthetic data in `tests/fixtures/`. No real genetic data is used or needed.

## Code Style

- Python 3.10+ with type hints on public functions
- Keep it simple. Avoid over-engineering.
- Match existing patterns in the codebase

## Making Changes

1. Fork the repo
2. Create a branch (`git checkout -b fix-something`)
3. Make your changes
4. Run tests (`pytest`)
5. Commit with a clear message
6. Open a pull request

## What to Contribute

**Good first issues:**
- Improve error messages
- Add tests for edge cases
- Documentation fixes

**Bigger contributions:**
- Support for AncestryDNA format
- New SNP annotations (with citations)
- Performance improvements

**Please discuss first:**
- Major architectural changes
- New commands or features
- External API integrations

## Adding SNP Annotations

The curated SNP database is in `src/genex/snpdb/curated.py`. To add annotations:

1. Include the rsid, gene, and category
2. Cite your source (ClinVar, PharmGKB, peer-reviewed paper)
3. Be conservative with clinical significance claims
4. Add a test if the SNP has special handling

## Privacy Requirements

- No network requests without explicit user opt-in
- No telemetry or analytics
- No logging of genetic data
- Tests must use synthetic data only

## Medical Disclaimer

Any health-related output must include appropriate disclaimers. We are not providing medical advice, and the code should make that clear to users.

## Questions?

Open an issue. Keep it brief.
