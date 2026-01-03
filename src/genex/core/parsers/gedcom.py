"""Parser for GEDCOM family tree files."""

from pathlib import Path
from typing import Optional
import re

from ..models import Individual, Family, Sex


def detect_gedcom(filepath: Path) -> bool:
    """Check if file is a valid GEDCOM file."""
    if not filepath.suffix.lower() == '.ged':
        return False
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            first_line = f.readline().strip()
            return first_line == '0 HEAD'
    except Exception:
        return False


def parse_gedcom(filepath: Path) -> tuple[dict[str, Individual], dict[str, Family]]:
    """
    Parse GEDCOM file and return individuals and families.

    Returns:
        Tuple of (individuals dict, families dict)
    """
    individuals: dict[str, Individual] = {}
    families: dict[str, Family] = {}

    current_record: Optional[Individual | Family] = None
    current_type: Optional[str] = None
    current_field: Optional[str] = None

    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            # Parse level, tag, and value
            parts = line.split(' ', 2)
            if not parts:
                continue

            try:
                level = int(parts[0])
            except ValueError:
                continue

            if level == 0:
                # New record
                if len(parts) >= 3 and parts[2] == 'INDI':
                    ind_id = parts[1]
                    current_record = Individual(id=ind_id)
                    individuals[ind_id] = current_record
                    current_type = 'INDI'
                elif len(parts) >= 3 and parts[2] == 'FAM':
                    fam_id = parts[1]
                    current_record = Family(id=fam_id)
                    families[fam_id] = current_record
                    current_type = 'FAM'
                else:
                    current_record = None
                    current_type = None
                current_field = None

            elif level == 1 and current_record:
                tag = parts[1] if len(parts) > 1 else ""
                value = parts[2] if len(parts) > 2 else ""

                if current_type == 'INDI' and isinstance(current_record, Individual):
                    if tag == 'NAME':
                        current_record.name = value.replace('/', '').strip()
                    elif tag == 'SEX':
                        if value == 'M':
                            current_record.sex = Sex.MALE
                        elif value == 'F':
                            current_record.sex = Sex.FEMALE
                    elif tag == 'BIRT':
                        current_field = 'BIRT'
                    elif tag == 'DEAT':
                        current_field = 'DEAT'
                    elif tag == 'FAMC':
                        current_record.family_child = value
                    elif tag == 'FAMS':
                        current_record.families_spouse.append(value)
                    else:
                        current_field = tag

                elif current_type == 'FAM' and isinstance(current_record, Family):
                    if tag == 'HUSB':
                        current_record.husband_id = value
                    elif tag == 'WIFE':
                        current_record.wife_id = value
                    elif tag == 'CHIL':
                        current_record.children.append(value)
                    elif tag == 'MARR':
                        current_field = 'MARR'
                    else:
                        current_field = tag

            elif level == 2 and current_record:
                tag = parts[1] if len(parts) > 1 else ""
                value = parts[2] if len(parts) > 2 else ""

                if current_type == 'INDI' and isinstance(current_record, Individual):
                    if tag == 'GIVN':
                        current_record.given_name = value
                    elif tag == 'SURN':
                        current_record.surname = value
                    elif tag == 'DATE' and current_field == 'BIRT':
                        current_record.birth_date = value
                    elif tag == 'PLAC' and current_field == 'BIRT':
                        current_record.birth_place = value
                    elif tag == 'DATE' and current_field == 'DEAT':
                        current_record.death_date = value
                    elif tag == 'PLAC' and current_field == 'DEAT':
                        current_record.death_place = value

                elif current_type == 'FAM' and isinstance(current_record, Family):
                    if tag == 'DATE' and current_field == 'MARR':
                        current_record.marriage_date = value
                    elif tag == 'PLAC' and current_field == 'MARR':
                        current_record.marriage_place = value

    return individuals, families


def count_individuals(filepath: Path) -> int:
    """Count individuals in GEDCOM file."""
    count = 0
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            if ' INDI' in line and line.strip().startswith('0 '):
                count += 1
    return count


def find_root_person(
    individuals: dict[str, Individual],
    families: dict[str, Family],
    name_hint: Optional[str] = None
) -> Optional[Individual]:
    """
    Find the root person in the tree.

    If name_hint is provided, search for that name.
    Otherwise, look for indicators like relationship_id='you'.
    """
    if name_hint:
        name_lower = name_hint.lower()
        for ind in individuals.values():
            if name_lower in ind.name.lower():
                return ind

    # Look for person with no children in any family (likely youngest generation)
    # who has the most complete data
    candidates = []
    for ind in individuals.values():
        if ind.family_child and ind.name:
            # Has parents and a name - potential root
            candidates.append(ind)

    # Sort by most complete data
    candidates.sort(
        key=lambda x: (
            bool(x.birth_date),
            bool(x.birth_place),
            len(x.name),
        ),
        reverse=True
    )

    return candidates[0] if candidates else None


def get_ancestors(
    person_id: str,
    individuals: dict[str, Individual],
    families: dict[str, Family],
    generation: int = 0,
    max_generations: int = 20
) -> list[tuple[int, Individual]]:
    """
    Get all ancestors of a person.

    Returns list of (generation, Individual) tuples.
    Generation 1 = parents, 2 = grandparents, etc.
    """
    if generation >= max_generations:
        return []

    ancestors = []
    person = individuals.get(person_id)

    if not person:
        return ancestors

    family_id = person.family_child
    if not family_id or family_id not in families:
        return ancestors

    family = families[family_id]

    # Add parents
    for parent_id in [family.husband_id, family.wife_id]:
        if parent_id and parent_id in individuals:
            parent = individuals[parent_id]
            ancestors.append((generation + 1, parent))
            # Recursively get their ancestors
            ancestors.extend(
                get_ancestors(parent_id, individuals, families, generation + 1, max_generations)
            )

    return ancestors
