#!/usr/bin/env python3
"""
Convert Sigma rules to Sumo Logic queries using sigma-cli with Splunk backend.
Splunk and Sumo Logic have similar query languages, so we use Splunk as a base
and make minimal adjustments for Sumo Logic compatibility.
"""
import json
import subprocess
import sys
from pathlib import Path

import yaml


SIGMA_RULES_DIR = Path(__file__).parent / "sigma_rules"


def install_splunk_backend():
    """Install the Splunk backend for sigma-cli."""
    print("Installing pySigma Splunk backend...")
    try:
        subprocess.run(
            ["sigma", "plugin", "install", "splunk"],
            check=True,
            capture_output=True,
            text=True
        )
        print("Splunk backend installed successfully")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not install Splunk backend: {e.stderr}")
        print("Continuing anyway - backend may already be installed")


def convert_sigma_rule(rule_path: Path) -> str:
    """Convert a Sigma rule to Sumo Logic query format using sigma-cli."""
    print(f"Converting {rule_path.name}...")

    try:
        # Use sigma-cli to convert to Splunk format (similar to Sumo Logic)
        result = subprocess.run(
            ["sigma", "convert", "-t", "splunk", "-f", "default", str(rule_path)],
            check=True,
            capture_output=True,
            text=True
        )

        splunk_query = result.stdout.strip()

        # Convert Splunk SPL to Sumo Logic query language
        # Both are very similar, but make some adjustments
        sumologic_query = convert_splunk_to_sumologic(splunk_query, rule_path)

        print(f"Successfully converted {rule_path.name}")
        return sumologic_query

    except subprocess.CalledProcessError as e:
        print(f"Error converting {rule_path.name}: {e.stderr}")
        raise Exception(f"Conversion failed: {e.stderr}")


def convert_splunk_to_sumologic(splunk_query: str, rule_path: Path) -> str:
    """
    Convert Splunk SPL to Sumo Logic query language.
    They are very similar, so minimal changes needed.
    """
    # Read the original Sigma rule to get metadata
    with open(rule_path, 'r', encoding='utf-8') as f:
        rule_data = yaml.safe_load(f)

    # Extract logsource information
    logsource = rule_data.get('logsource', {})
    product = logsource.get('product', '')
    service = logsource.get('service', '')

    # Build Sumo Logic query
    # Start with _sourceCategory filter based on product/service
    if product and service:
        source_category = f'_sourceCategory="{product}/{service}"'
    elif product:
        source_category = f'_sourceCategory="{product}"'
    else:
        source_category = ''

    # Combine source category with the converted query
    if source_category and splunk_query:
        sumologic_query = f"{source_category} {splunk_query}"
    elif splunk_query:
        sumologic_query = splunk_query
    else:
        # Fallback: create basic query from detection logic
        sumologic_query = create_basic_sumologic_query(rule_data)

    return sumologic_query


def create_basic_sumologic_query(rule_data: dict) -> str:
    """
    Create a basic Sumo Logic query from Sigma rule detection logic.
    This is a fallback when sigma-cli conversion doesn't work.
    """
    logsource = rule_data.get('logsource', {})
    detection = rule_data.get('detection', {})

    # Start with source category
    product = logsource.get('product', 'unknown')
    parts = [f'_sourceCategory="{product}"']

    # Add selection criteria
    selection = detection.get('selection', {})
    for field, value in selection.items():
        if isinstance(value, str):
            parts.append(f'{field}="{value}"')
        elif isinstance(value, list):
            # Multiple values - use OR
            value_conditions = [f'{field}="{v}"' for v in value]
            parts.append(f'({" OR ".join(value_conditions)})')

    # Add filters (negations)
    filter_def = detection.get('filter', {})
    for field, value in filter_def.items():
        if isinstance(value, str):
            parts.append(f'!{field}="{value}"')

    return '\n| where ' + ' AND '.join(parts) if len(parts) > 1 else parts[0]


def main():
    """Main conversion process."""
    print("Sigma to Sumo Logic Converter (using sigma-cli)")
    print("=" * 50)

    # Install Splunk backend
    install_splunk_backend()

    # Find all Sigma rules
    sigma_files = list(SIGMA_RULES_DIR.glob("*.yml")) + list(SIGMA_RULES_DIR.glob("*.yaml"))

    if not sigma_files:
        print(f"No Sigma rules found in {SIGMA_RULES_DIR}")
        sys.exit(1)

    print(f"\nFound {len(sigma_files)} Sigma rule(s)")

    # Convert each rule
    converted_rules = {}
    for rule_file in sigma_files:
        try:
            query = convert_sigma_rule(rule_file)
            converted_rules[rule_file.stem] = {
                "file": rule_file.name,
                "query": query
            }
        except Exception as e:
            print(f"Failed to convert {rule_file.name}: {e}")
            sys.exit(1)

    # Save converted rules to JSON
    output_file = Path(__file__).parent / "converted_rules.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(converted_rules, f, indent=2)

    print(f"\nSuccessfully converted {len(converted_rules)} rule(s)")
    print(f"Output saved to: {output_file}")

    # Print converted queries
    print("\n" + "=" * 50)
    print("Converted Queries")
    print("=" * 50)
    for rule_name, data in converted_rules.items():
        print(f"\n{rule_name}:")
        print(f"  File: {data['file']}")
        print(f"  Query:\n{data['query']}")


if __name__ == "__main__":
    main()
