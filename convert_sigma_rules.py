#!/usr/bin/env python3
"""
Convert Sigma rules to Splunk SPL queries using sigma-cli.
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
    """Convert a Sigma rule to Splunk SPL query format using sigma-cli."""
    print(f"Converting {rule_path.name}...")

    try:
        # Use sigma-cli to convert to Splunk format
        result = subprocess.run(
            ["sigma", "convert", "-t", "splunk", "-f", "default", str(rule_path)],
            check=True,
            capture_output=True,
            text=True
        )

        splunk_query = result.stdout.strip()

        if not splunk_query:
            # Fallback: create basic query from detection logic
            print(f"  Using fallback converter for {rule_path.name}")
            splunk_query = create_basic_splunk_query(rule_path)

        print(f"Successfully converted {rule_path.name}")
        return splunk_query

    except subprocess.CalledProcessError as e:
        print(f"Error converting {rule_path.name}: {e.stderr}")
        print(f"  Using fallback converter")
        return create_basic_splunk_query(rule_path)


def create_basic_splunk_query(rule_path: Path) -> str:
    """
    Create a basic Splunk SPL query from Sigma rule detection logic.
    This is a fallback when sigma-cli conversion doesn't work.
    """
    with open(rule_path, 'r', encoding='utf-8') as f:
        rule_data = yaml.safe_load(f)

    logsource = rule_data.get('logsource', {})
    detection = rule_data.get('detection', {})

    # Start with source/sourcetype based on product/service
    product = logsource.get('product', '')
    service = logsource.get('service', '')

    parts = []

    if product and service:
        parts.append(f'source="{product}" sourcetype="{service}"')
    elif product:
        parts.append(f'sourcetype="{product}"')

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
            parts.append(f'NOT {field}="{value}"')

    # Combine all parts
    if parts:
        return 'search ' + ' '.join(parts)
    else:
        return 'search *'


def main():
    """Main conversion process."""
    print("Sigma to Splunk SPL Converter (using sigma-cli)")
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
        print(f"  Query:\n    {data['query']}")


if __name__ == "__main__":
    main()
