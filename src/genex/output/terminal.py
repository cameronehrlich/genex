"""Rich terminal output formatting for genex."""

from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box

from ..core.models import SNP, SNPAnnotation, HealthFinding, RiskLevel, Individual
from ..analysis.health import APOEStatus


console = Console()

# Medical disclaimer
MEDICAL_DISCLAIMER = """
[dim]Note: This is informational only, not medical advice. Genetic variants
indicate probabilities, not certainties. Discuss any concerns with a
healthcare provider or genetic counselor.[/dim]
"""


def print_header(title: str):
    """Print a section header."""
    console.print()
    console.print(f"[bold blue]{title}[/bold blue]")
    console.print("=" * len(title))


def print_snp(snp: SNP, annotation: Optional[SNPAnnotation] = None):
    """Print a single SNP with optional annotation."""
    console.print(f"\n[bold]{snp.rsid}[/bold]", end="")
    if annotation:
        console.print(f" ([cyan]{annotation.gene}[/cyan])")
    else:
        console.print()

    console.print(f"  Chromosome: {snp.chromosome}")
    console.print(f"  Position:   {snp.position:,}")
    console.print(f"  Genotype:   [bold]{snp.genotype}[/bold]")

    if annotation:
        console.print()
        if annotation.description:
            console.print(f"  [dim]{annotation.description}[/dim]")
        if annotation.condition:
            console.print(f"  Condition: {annotation.condition}")
        if annotation.drugs:
            console.print(f"  Drugs: {annotation.drugs}")


def print_apoe_status(status: APOEStatus):
    """Print APOE status with appropriate styling."""
    print_header("APOE STATUS (Alzheimer's Risk)")

    # Color based on risk
    if status.risk_level == RiskLevel.HIGH:
        color = "red"
    elif status.risk_level == RiskLevel.ELEVATED:
        color = "yellow"
    elif status.risk_level == RiskLevel.NORMAL:
        color = "green"
    else:
        color = "white"

    console.print(f"\n  Genotype: [bold {color}]{status.genotype}[/bold {color}]")
    console.print(f"  {status.interpretation}")
    console.print(f"\n  [dim]rs429358={status.rs429358}, rs7412={status.rs7412}[/dim]")


def print_health_findings(findings: list[HealthFinding]):
    """Print health findings table."""
    print_header("HEALTH VARIANTS")

    # Group by risk level
    high_risk = [f for f in findings if f.risk_level == RiskLevel.HIGH]
    elevated = [f for f in findings if f.risk_level in (RiskLevel.ELEVATED, RiskLevel.CARRIER)]
    normal = [f for f in findings if f.risk_level == RiskLevel.NORMAL]

    if high_risk:
        console.print("\n[bold red]High Risk Findings:[/bold red]")
        for finding in high_risk:
            _print_finding(finding, "red")

    if elevated:
        console.print("\n[bold yellow]Elevated/Carrier Status:[/bold yellow]")
        for finding in elevated:
            _print_finding(finding, "yellow")

    if normal:
        console.print("\n[green]Normal Results:[/green]")
        for finding in normal:
            _print_finding(finding, "green")

    console.print(MEDICAL_DISCLAIMER)


def _print_finding(finding: HealthFinding, color: str):
    """Print a single health finding."""
    icon = "!" if color == "red" else ("*" if color == "yellow" else "✓")
    console.print(f"\n  [{color}]{icon}[/{color}] [bold]{finding.annotation.gene}[/bold] ({finding.snp.rsid})")
    console.print(f"    {finding.interpretation}")
    if finding.annotation.condition:
        console.print(f"    [dim]Condition: {finding.annotation.condition}[/dim]")
    if finding.recommendation:
        console.print(f"    [cyan]Recommendation: {finding.recommendation}[/cyan]")


def print_pharma_table(findings: list[HealthFinding]):
    """Print pharmacogenomics table."""
    print_header("PHARMACOGENOMICS")

    table = Table(box=box.ROUNDED)
    table.add_column("Gene", style="cyan")
    table.add_column("Variant")
    table.add_column("Genotype")
    table.add_column("Status")
    table.add_column("Affected Drugs", style="dim")

    for finding in findings:
        status_color = "green" if finding.risk_level == RiskLevel.NORMAL else "yellow"
        status_text = finding.interpretation.split(" for ")[0] if " for " in finding.interpretation else finding.interpretation

        table.add_row(
            finding.annotation.gene,
            finding.annotation.description[:30] + "..." if len(finding.annotation.description) > 30 else finding.annotation.description,
            finding.snp.genotype,
            f"[{status_color}]{status_text}[/{status_color}]",
            finding.annotation.drugs or "",
        )

    console.print(table)
    console.print("\n[dim]Consult your doctor before making any medication changes.[/dim]")


def print_traits_table(findings: list[HealthFinding]):
    """Print traits table."""
    print_header("TRAITS & WELLNESS")

    for finding in findings:
        trait = finding.annotation.condition or finding.annotation.description
        interpretation = _interpret_trait(finding)
        console.print(f"\n  [bold]{trait}[/bold]")
        console.print(f"    {interpretation}")
        console.print(f"    [dim]({finding.snp.rsid}: {finding.snp.genotype})[/dim]")


def _interpret_trait(finding: HealthFinding) -> str:
    """Get human-readable trait interpretation."""
    rsid = finding.snp.rsid
    genotype = finding.snp.genotype

    interpretations = {
        "rs762551": {
            "AA": "Fast caffeine metabolizer",
            "AC": "Slow caffeine metabolizer",
            "CC": "Slow caffeine metabolizer",
        },
        "rs4988235": {
            "TT": "Lactose tolerant",
            "CT": "Likely lactose tolerant",
            "CC": "Likely lactose intolerant",
        },
        "rs671": {
            "GG": "No alcohol flush reaction",
            "AG": "Alcohol flush reaction",
            "AA": "Strong alcohol flush reaction",
        },
        "rs1815739": {
            "CC": "Power/sprint muscle type",
            "CT": "Mixed muscle type",
            "TT": "Endurance muscle type",
        },
        "rs72921001": {
            "CC": "Normal cilantro taste",
            "AC": "May taste cilantro as soapy",
            "AA": "Likely tastes cilantro as soapy",
        },
        "rs12913832": {
            "GG": "Blue eyes likely",
            "AG": "Green/hazel eyes possible",
            "AA": "Brown eyes likely",
        },
        "rs17822931": {
            "CC": "Dry earwax",
            "CT": "Wet earwax",
            "TT": "Wet earwax",
        },
    }

    if rsid in interpretations and genotype in interpretations[rsid]:
        return interpretations[rsid][genotype]
    return f"Genotype: {genotype}"


def print_ancestry_summary(ancestry_data: dict):
    """Print ancestry composition summary."""
    print_header("ANCESTRY COMPOSITION")

    copy1 = ancestry_data.get('copy1', {})
    copy2 = ancestry_data.get('copy2', {})

    if copy1:
        console.print("\n[bold]Copy 1 (Parental):[/bold]")
        _print_ancestry_bars(copy1)

    if copy2:
        console.print("\n[bold]Copy 2 (Parental):[/bold]")
        _print_ancestry_bars(copy2)


def _print_ancestry_bars(data: dict):
    """Print ancestry bars for one copy."""
    # Filter to top-level ancestries (skip sub-categories if parent exists)
    total = sum(data.values())
    if total == 0:
        return

    for ancestry, length in sorted(data.items(), key=lambda x: -x[1]):
        pct = (length / total) * 100
        if pct > 1:  # Only show >1%
            bar_width = int(pct / 5)  # Scale to ~20 chars max
            bar = "█" * bar_width
            console.print(f"  {bar} {ancestry} ({pct:.1f}%)")


def print_tree_summary(individual_count: int, family_count: int, root: Optional[Individual] = None):
    """Print family tree summary."""
    print_header("FAMILY TREE")

    console.print(f"\n  Individuals: {individual_count}")
    console.print(f"  Families: {family_count}")

    if root:
        console.print(f"\n  [bold]Root person:[/bold] {root.name}")
        if root.birth_date:
            console.print(f"  Born: {root.birth_date}")
        if root.birth_place:
            console.print(f"  Place: {root.birth_place}")


def print_ancestors(ancestors: list[tuple[int, Individual]]):
    """Print ancestor list by generation."""
    print_header("ANCESTORS")

    gen_names = {
        1: "Parents",
        2: "Grandparents",
        3: "Great-grandparents",
        4: "2x Great-grandparents",
        5: "3x Great-grandparents",
        6: "4x Great-grandparents",
    }

    # Group by generation
    by_gen: dict[int, list[Individual]] = {}
    for gen, ind in ancestors:
        if gen not in by_gen:
            by_gen[gen] = []
        by_gen[gen].append(ind)

    for gen in sorted(by_gen.keys()):
        gen_label = gen_names.get(gen, f"Gen {gen}")
        console.print(f"\n[bold]{gen_label}[/bold] ({len(by_gen[gen])} known):")

        for ind in by_gen[gen]:
            line = f"  • {ind.name}"
            if ind.birth_date:
                line += f" (b. {ind.birth_date})"
            if ind.birth_place:
                line += f" - {ind.birth_place}"
            if ind.death_date:
                line += f" [dim]d. {ind.death_date}[/dim]"
            console.print(line)


def print_error(message: str):
    """Print error message."""
    console.print(f"[red]Error:[/red] {message}")


def print_success(message: str):
    """Print success message."""
    console.print(f"[green]✓[/green] {message}")


def print_warning(message: str):
    """Print warning message."""
    console.print(f"[yellow]⚠[/yellow] {message}")
