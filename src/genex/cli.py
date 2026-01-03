"""Command-line interface for genex."""

import click
from pathlib import Path
from typing import Optional
import sys

from .core.database import GenexDatabase
from .core.models import DataSource, GenomeBuild
from .core.parsers.twentythree import (
    detect_23andme, parse_23andme_genome, count_snps as count_23andme_snps,
    parse_ancestry_composition
)
from .core.parsers.gedcom import (
    detect_gedcom, parse_gedcom, count_individuals as count_gedcom_individuals,
)
from .snpdb.curated import get_all_annotations, SNPDB_VERSION
from .analysis.health import determine_apoe_status, run_health_analysis, analyze_health_snp
from .output import terminal


# Default paths
DEFAULT_GENEX_DIR = Path.home() / ".genex"
DEFAULT_DB_PATH = DEFAULT_GENEX_DIR / "genex.db"


def get_db() -> GenexDatabase:
    """Get database instance, ensuring it exists."""
    if not DEFAULT_DB_PATH.exists():
        terminal.print_error("No genex database found. Run 'genex init <data_dir>' first.")
        sys.exit(1)
    return GenexDatabase(DEFAULT_DB_PATH)


@click.group()
@click.version_option(version="0.1.0", prog_name="genex")
def main():
    """genex - Privacy-first genetic data explorer.

    Explore your 23andMe, AncestryDNA, and GEDCOM data locally.
    All processing happens on your machine. Your data never leaves.
    """
    pass


@main.command()
@click.argument('data_dir', type=click.Path(exists=True, path_type=Path))
@click.option('--force', is_flag=True, help='Force re-import, replacing existing data')
def init(data_dir: Path, force: bool):
    """Initialize genex with genetic data from DATA_DIR.

    Scans the directory for 23andMe files, GEDCOM family trees,
    and ancestry composition data.
    """
    terminal.console.print(f"Scanning [cyan]{data_dir}[/cyan]...")

    # Ensure genex directory exists
    DEFAULT_GENEX_DIR.mkdir(parents=True, exist_ok=True)

    # Check if database exists
    if DEFAULT_DB_PATH.exists() and not force:
        terminal.print_warning("Database already exists. Use --force to re-import.")

    # Create/reset database
    db = GenexDatabase(DEFAULT_DB_PATH)

    # Load curated annotations
    terminal.console.print("Loading SNP annotation database...")
    annotations = get_all_annotations()
    db.insert_annotations_batch(annotations)
    db.set_metadata("snpdb_version", SNPDB_VERSION)

    found_files = []

    # Scan for files
    for filepath in data_dir.rglob("*"):
        if filepath.is_dir():
            continue

        # Check for 23andMe genome file
        if filepath.suffix in ('.txt', '.zip') and detect_23andme(filepath):
            terminal.console.print(f"  [green]✓[/green] 23andMe genome file: {filepath.name}")
            snp_count = count_23andme_snps(filepath)
            terminal.console.print(f"    Loading {snp_count:,} SNPs...")

            snps = parse_23andme_genome(filepath)
            db.insert_snps_batch(snps)
            db.set_metadata("genome_source", filepath.name)
            found_files.append(("23andMe genome", filepath.name, snp_count))

        # Check for ancestry composition
        elif filepath.suffix == '.csv' and 'ancestry' in filepath.name.lower():
            try:
                segments = list(parse_ancestry_composition(filepath))
                if segments:
                    terminal.console.print(f"  [green]✓[/green] Ancestry composition: {filepath.name}")
                    db.insert_ancestry_segments(iter(segments))
                    found_files.append(("Ancestry", filepath.name, len(segments)))
            except Exception:
                pass

        # Check for GEDCOM
        elif detect_gedcom(filepath):
            terminal.console.print(f"  [green]✓[/green] GEDCOM family tree: {filepath.name}")
            ind_count = count_gedcom_individuals(filepath)
            terminal.console.print(f"    Loading {ind_count} individuals...")

            individuals, families = parse_gedcom(filepath)
            for ind in individuals.values():
                db.insert_individual(ind)
            for fam in families.values():
                db.insert_family(fam)
            db.set_metadata("gedcom_source", filepath.name)
            found_files.append(("GEDCOM", filepath.name, ind_count))

    if not found_files:
        terminal.print_warning("No recognized genetic data files found.")
        return

    terminal.console.print()
    terminal.print_success(f"Initialized genex database at {DEFAULT_DB_PATH}")

    # Summary
    terminal.console.print("\n[bold]Summary:[/bold]")
    for file_type, name, count in found_files:
        terminal.console.print(f"  {file_type}: {count:,} records")


@main.command()
@click.argument('rsid')
@click.option('--raw', is_flag=True, help='Output just the genotype')
@click.option('--provenance', is_flag=True, help='Show annotation sources')
def snp(rsid: str, raw: bool, provenance: bool):
    """Look up a specific SNP by rsid.

    Example: genex snp rs429358
    """
    db = get_db()

    snp_data = db.get_snp(rsid)
    if not snp_data:
        terminal.print_error(f"SNP {rsid} not found in your data.")
        return

    if raw:
        click.echo(snp_data.genotype)
        return

    annotation = db.get_annotation(rsid)
    terminal.print_snp(snp_data, annotation)

    if provenance and annotation:
        terminal.console.print(f"\n  [dim]Source: {annotation.source} v{annotation.source_version}[/dim]")


@main.command()
@click.option('--category', type=click.Choice(['all', 'cardiovascular', 'cancer', 'carrier']),
              default='all', help='Filter by category')
@click.option('--detail', is_flag=True, help='Show detailed output')
def health(category: str, detail: bool):
    """Analyze health-related genetic variants.

    Checks APOE (Alzheimer's), cardiovascular risk, cancer genes,
    and carrier status for inherited conditions.
    """
    db = get_db()

    # APOE is special - always show
    apoe = determine_apoe_status(db)
    terminal.print_apoe_status(apoe)

    # Run health analysis
    findings = run_health_analysis(db)

    if category != 'all':
        # Filter by category
        category_map = {
            'cardiovascular': ['Factor V Leiden', 'Prothrombin', 'Hemochromatosis'],
            'cancer': ['BRCA', 'Hereditary Breast'],
            'carrier': [],  # Use carrier panel
        }
        if category == 'carrier':
            # Get carrier annotations
            carrier_annotations = db.get_annotations_by_category('carrier')
            rsids = [a.rsid for a in carrier_annotations]
            snps = db.get_snps_by_rsids(rsids)
            findings = []
            for ann in carrier_annotations:
                snp_data = snps.get(ann.rsid)
                if snp_data and snp_data.is_called:
                    findings.append(analyze_health_snp(snp_data, ann))
        else:
            keywords = category_map.get(category, [])
            findings = [f for f in findings
                       if any(kw.lower() in (f.annotation.condition or '').lower() for kw in keywords)]

    if findings:
        terminal.print_health_findings(findings)
    else:
        terminal.console.print("\n[dim]No findings in this category.[/dim]")


@main.command()
def pharma():
    """Show pharmacogenomics (drug metabolism) profile.

    Analyzes how you metabolize common medications including
    blood thinners, statins, antidepressants, and pain medications.
    """
    db = get_db()

    # Get pharma annotations
    annotations = db.get_annotations_by_category('pharma')
    rsids = [a.rsid for a in annotations]
    snps = db.get_snps_by_rsids(rsids)

    findings = []
    for ann in annotations:
        snp_data = snps.get(ann.rsid)
        if snp_data and snp_data.is_called:
            findings.append(analyze_health_snp(snp_data, ann))

    if findings:
        terminal.print_pharma_table(findings)
    else:
        terminal.print_warning("No pharmacogenomic data found.")


@main.command()
def traits():
    """Analyze trait-related genetic variants.

    Shows caffeine metabolism, lactose tolerance, muscle type,
    taste perception, and other trait-related variants.
    """
    db = get_db()

    # Get trait annotations
    annotations = db.get_annotations_by_category('trait')
    rsids = [a.rsid for a in annotations]
    snps = db.get_snps_by_rsids(rsids)

    findings = []
    for ann in annotations:
        snp_data = snps.get(ann.rsid)
        if snp_data and snp_data.is_called:
            findings.append(analyze_health_snp(snp_data, ann))

    if findings:
        terminal.print_traits_table(findings)
    else:
        terminal.print_warning("No trait data found.")


@main.command()
def ancestry():
    """Show ancestry composition summary.

    Displays chromosome-by-chromosome ancestry breakdown
    from your genetic data.
    """
    db = get_db()

    data = db.get_ancestry_summary()

    if not data['copy1'] and not data['copy2']:
        terminal.print_warning("No ancestry composition data found.")
        terminal.console.print("[dim]Make sure you imported an ancestry composition file.[/dim]")
        return

    terminal.print_ancestry_summary(data)


@main.group()
def tree():
    """Family tree commands.

    Explore your GEDCOM family tree data.
    """
    pass


@tree.command('summary')
def tree_summary():
    """Show family tree summary."""
    db = get_db()

    ind_count = db.count_individuals()
    if ind_count == 0:
        terminal.print_warning("No family tree data found.")
        terminal.console.print("[dim]Import a GEDCOM file with 'genex init'.[/dim]")
        return

    root_person = db.find_root_individual()
    terminal.print_tree_summary(ind_count, 0, root_person)


@tree.command('ancestors')
@click.option('--name', help='Name of person to find ancestors for')
@click.option('--generations', '-g', default=10, show_default=True, help='Max generations to show')
def tree_ancestors(name: Optional[str], generations: int):
    """List ancestors by generation."""
    db = get_db()

    person = None
    if name:
        matches = db.search_individuals(name)
        if not matches:
            terminal.print_warning(f"No individuals found matching '{name}'.")
            terminal.console.print("[dim]Try 'genex tree search' to confirm the exact name.[/dim]")
            return
        person = matches[0]
        if len(matches) > 1:
            terminal.console.print(
                f"[dim]Multiple matches found; showing ancestors for {person.name}. "
                "Use a more specific name to narrow it down.[/dim]"
            )
    else:
        person = db.find_root_individual()
        if not person:
            terminal.print_warning("Could not determine a root person in your tree.")
            terminal.console.print("[dim]Use --name to pick a person with known parents.[/dim]")
            return

    max_generations = max(1, generations)
    ancestors = db.get_ancestors(person.id, max_generations)

    if not ancestors:
        terminal.print_warning(f"No ancestors found for {person.name}.")
        terminal.console.print("[dim]Make sure this person has parents in the GEDCOM data.[/dim]")
        return

    terminal.console.print(f"\n[bold]Ancestors for:[/bold] {person.name}")
    terminal.print_ancestors(ancestors)


@tree.command('search')
@click.argument('query')
def tree_search(query: str):
    """Search family tree for individuals.

    Example: genex tree search "Berlin"
    """
    db = get_db()

    results = db.search_individuals(query)

    if not results:
        terminal.console.print(f"No individuals found matching '{query}'")
        return

    terminal.console.print(f"\n[bold]Found {len(results)} matches:[/bold]")
    for ind in results[:20]:  # Limit to 20
        line = f"  • {ind.name}"
        if ind.birth_date:
            line += f" (b. {ind.birth_date})"
        if ind.birth_place:
            line += f" - {ind.birth_place}"
        terminal.console.print(line)

    if len(results) > 20:
        terminal.console.print(f"  [dim]...and {len(results) - 20} more[/dim]")


@main.command()
def status():
    """Show genex status and loaded data summary."""
    if not DEFAULT_DB_PATH.exists():
        terminal.print_error("No genex database found. Run 'genex init <data_dir>' first.")
        return

    db = get_db()

    terminal.console.print("\n[bold]genex status[/bold]")
    terminal.console.print(f"  Database: {DEFAULT_DB_PATH}")

    snp_count = db.count_snps()
    ind_count = db.count_individuals()
    snpdb_version = db.get_metadata("snpdb_version") or "unknown"
    genome_source = db.get_metadata("genome_source") or "none"
    gedcom_source = db.get_metadata("gedcom_source") or "none"

    terminal.console.print(f"\n[bold]Data loaded:[/bold]")
    terminal.console.print(f"  SNPs: {snp_count:,}")
    terminal.console.print(f"  Individuals: {ind_count}")

    terminal.console.print(f"\n[bold]Sources:[/bold]")
    terminal.console.print(f"  Genome: {genome_source}")
    terminal.console.print(f"  Family tree: {gedcom_source}")
    terminal.console.print(f"  Annotation DB: v{snpdb_version}")


if __name__ == "__main__":
    main()
