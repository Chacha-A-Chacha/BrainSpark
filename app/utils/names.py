# app/utils/names.py
import re
from pathlib import Path
from typing import List


def load_animal_names(file_path: Path) -> List[str]:
    """Load and process animal names from a text file with mixed formatting."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()

        # Split names while handling parentheses and comma-separated values
        names = []
        current_group = []
        in_parentheses = False

        for part in re.split(r',|\((.*?)\)', content):
            part = part.strip()
            if not part:
                continue

            if part.startswith('('):
                in_parentheses = True
                part = part[1:]

            if in_parentheses:
                if ')' in part:
                    in_parentheses = False
                    part = part.replace(')', '')
                current_group.append(part)
                if not in_parentheses:
                    names.append(' '.join(current_group).title())
                    current_group = []
            else:
                if current_group:
                    names.append(' '.join(current_group).title())
                    current_group = []
                current_group.append(part)

        # Process remaining group
        if current_group:
            names.append(' '.join(current_group).title())

        # Clean and deduplicate
        cleaned_names = []
        seen = set()
        for name in names:
            # Remove special characters and normalize whitespace
            clean_name = re.sub(r'[^a-zA-Z\s]', '', name).strip()
            if clean_name and clean_name.lower() not in seen:
                seen.add(clean_name.lower())
                cleaned_names.append(clean_name)

        return sorted(cleaned_names, key=lambda x: x.lower())

    except Exception as e:
        raise RuntimeError(f"Error processing animal names: {str(e)}")


def generate_animal_name() -> str:
    """Generate a random animal name from the processed list."""
    from random import choice
    data_file = Path(__file__).parent / 'data' / 'animal_names.txt'
    names = load_animal_names(data_file)
    adjectives = ["Red", "Swift", "Clever", "Mighty", "Golden", "Silver"]
    return f"{choice(adjectives)}{choice(names)}"
