#!/usr/bin/env python3
"""
Convert Sigma rules to Sumo Logic queries using sigconverter.io API.
"""
import base64
import json
import os
import sys
import time
from pathlib import Path
from typing import Dict, List

import requests


SIGMA_RULES_DIR = Path(__file__).parent / "sigma_rules"
SIGCONVERTER_URL = os.getenv("SIGCONVERTER_URL", "http://localhost:8000")
TARGET_BACKEND = "sumologic"
OUTPUT_FORMAT = "default"


def wait_for_sigconverter(max_retries: int = 30, delay: int = 2) -> bool:
    """Wait for sigconverter API to be ready."""
    print(f"Waiting for sigconverter at {SIGCONVERTER_URL}...")
    for i in range(max_retries):
        try:
            response = requests.get(f"{SIGCONVERTER_URL}/api/v1/targets", timeout=5)
            if response.status_code == 200:
                print("Sigconverter is ready!")
                return True
        except requests.exceptions.RequestException:
            pass

        if i < max_retries - 1:
            print(f"Attempt {i + 1}/{max_retries} failed, retrying in {delay}s...")
            time.sleep(delay)

    print("Failed to connect to sigconverter")
    return False


def get_available_targets() -> List[Dict]:
    """Get list of available conversion targets."""
    response = requests.get(f"{SIGCONVERTER_URL}/api/v1/targets")
    response.raise_for_status()
    return response.json()


def convert_sigma_rule(rule_path: Path) -> str:
    """Convert a Sigma rule to Sumo Logic query format."""
    print(f"Converting {rule_path.name}...")

    # Read the Sigma rule
    with open(rule_path, 'r', encoding='utf-8') as f:
        rule_yaml = f.read()

    # Encode rule as base64
    rule_b64 = base64.b64encode(rule_yaml.encode()).decode()

    # Prepare API request
    payload = {
        "rule": rule_b64,
        "target": TARGET_BACKEND,
        "format": OUTPUT_FORMAT,
        "pipeline": [],
        "pipelineYml": None,
        "html": "false"
    }

    # Call conversion API
    response = requests.post(
        f"{SIGCONVERTER_URL}/api/v1/convert",
        json=payload,
        headers={"Content-Type": "application/json"}
    )

    if response.status_code != 200:
        print(f"Error converting {rule_path.name}: {response.text}")
        raise Exception(f"Conversion failed: {response.text}")

    converted_query = response.text
    print(f"Successfully converted {rule_path.name}")
    return converted_query


def main():
    """Main conversion process."""
    # Wait for sigconverter to be ready
    if not wait_for_sigconverter():
        print("Error: Sigconverter not available")
        sys.exit(1)

    # Check if Sumo Logic target is available
    targets = get_available_targets()
    target_names = [t.get('name') for t in targets]

    print(f"Available targets: {', '.join(target_names)}")

    if TARGET_BACKEND not in target_names:
        print(f"Warning: '{TARGET_BACKEND}' backend not found in available targets")
        print(f"Available backends: {target_names}")
        # Continue anyway in case backend name is slightly different

    # Find all Sigma rules
    sigma_files = list(SIGMA_RULES_DIR.glob("*.yml")) + list(SIGMA_RULES_DIR.glob("*.yaml"))

    if not sigma_files:
        print(f"No Sigma rules found in {SIGMA_RULES_DIR}")
        sys.exit(1)

    print(f"Found {len(sigma_files)} Sigma rule(s)")

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
    print("\n=== Converted Queries ===")
    for rule_name, data in converted_rules.items():
        print(f"\n{rule_name}:")
        print(f"  File: {data['file']}")
        print(f"  Query: {data['query']}")


if __name__ == "__main__":
    main()
