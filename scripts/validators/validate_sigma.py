#!/usr/bin/env python3
"""
Sigma Rule Validator

This script validates Sigma detection rules for:
- YAML syntax correctness
- Required fields presence
- Schema compliance
- Field naming conventions
"""

import yaml
import sys
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
import uuid


class SigmaValidator:
    """Validates Sigma rules against schema and best practices."""

    REQUIRED_FIELDS = ['title', 'id', 'description', 'logsource', 'detection', 'level']
    OPTIONAL_FIELDS = ['status', 'author', 'references', 'tags', 'falsepositives', 'date', 'modified']
    VALID_LEVELS = ['critical', 'high', 'medium', 'low', 'informational']
    VALID_STATUSES = ['stable', 'test', 'experimental', 'deprecated', 'unsupported']

    def __init__(self):
        self.errors = []
        self.warnings = []

    def validate_yaml_syntax(self, file_path: Path) -> Tuple[bool, Any]:
        """Validate YAML syntax."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            return True, data
        except yaml.YAMLError as e:
            self.errors.append(f"YAML syntax error: {e}")
            return False, None
        except Exception as e:
            self.errors.append(f"Error reading file: {e}")
            return False, None

    def validate_required_fields(self, rule: Dict[str, Any]) -> bool:
        """Check if all required fields are present."""
        valid = True
        for field in self.REQUIRED_FIELDS:
            if field not in rule:
                self.errors.append(f"Missing required field: {field}")
                valid = False
        return valid

    def validate_uuid(self, rule_id: str) -> bool:
        """Validate UUID format."""
        try:
            uuid.UUID(rule_id)
            return True
        except ValueError:
            self.errors.append(f"Invalid UUID format: {rule_id}")
            return False

    def validate_level(self, level: str) -> bool:
        """Validate severity level."""
        if level not in self.VALID_LEVELS:
            self.errors.append(
                f"Invalid level '{level}'. Must be one of: {', '.join(self.VALID_LEVELS)}"
            )
            return False
        return True

    def validate_status(self, status: str) -> bool:
        """Validate rule status."""
        if status not in self.VALID_STATUSES:
            self.warnings.append(
                f"Non-standard status '{status}'. Recommended: {', '.join(self.VALID_STATUSES)}"
            )
            return False
        return True

    def validate_logsource(self, logsource: Dict[str, str]) -> bool:
        """Validate logsource structure."""
        valid = True

        if not isinstance(logsource, dict):
            self.errors.append("logsource must be a dictionary")
            return False

        # Check for at least one logsource field
        if not any(key in logsource for key in ['product', 'category', 'service']):
            self.errors.append(
                "logsource must contain at least one of: product, category, service"
            )
            valid = False

        # Validate known products
        known_products = ['windows', 'linux', 'macos', 'aws', 'azure', 'gcp', 'kubernetes']
        if 'product' in logsource and logsource['product'] not in known_products:
            self.warnings.append(
                f"Uncommon product '{logsource['product']}'. Consider using: {', '.join(known_products)}"
            )

        return valid

    def validate_detection(self, detection: Dict[str, Any]) -> bool:
        """Validate detection logic structure."""
        valid = True

        if not isinstance(detection, dict):
            self.errors.append("detection must be a dictionary")
            return False

        # Must have condition
        if 'condition' not in detection:
            self.errors.append("detection must contain 'condition' field")
            valid = False

        # Should have at least one selection
        selection_keys = [k for k in detection.keys() if k != 'condition']
        if not selection_keys:
            self.errors.append("detection must contain at least one selection")
            valid = False

        # Validate condition references
        if 'condition' in detection:
            condition = detection['condition']
            # Extract selection names from condition
            referenced_selections = re.findall(r'\b(\w+)\b', condition)
            for ref in referenced_selections:
                # Skip logic keywords
                if ref in ['and', 'or', 'not', 'of', 'all', '1']:
                    continue
                # Check if selection exists
                if ref not in detection:
                    self.warnings.append(
                        f"Condition references '{ref}' but no such selection exists"
                    )

        return valid

    def validate_tags(self, tags: List[str]) -> bool:
        """Validate MITRE ATT&CK tags."""
        valid = True

        if not isinstance(tags, list):
            self.errors.append("tags must be a list")
            return False

        # Check for MITRE ATT&CK tags
        mitre_tags = [tag for tag in tags if tag.startswith('attack.')]
        if not mitre_tags:
            self.warnings.append(
                "No MITRE ATT&CK tags found. Consider adding attack.* tags"
            )

        # Validate MITRE tag format
        technique_pattern = re.compile(r'^attack\.t\d{4}(\.\d{3})?$')
        for tag in mitre_tags:
            if not tag.startswith('attack.t') and not '.' in tag[7:]:
                # It's a tactic tag, which is okay
                continue
            if tag.startswith('attack.t') and not technique_pattern.match(tag):
                self.warnings.append(
                    f"Malformed MITRE technique tag: {tag}"
                )

        return valid

    def validate_rule(self, rule: Dict[str, Any]) -> bool:
        """Run all validation checks on a rule."""
        valid = True

        # Required fields
        if not self.validate_required_fields(rule):
            valid = False

        # UUID format
        if 'id' in rule:
            if not self.validate_uuid(rule['id']):
                valid = False

        # Level
        if 'level' in rule:
            if not self.validate_level(rule['level']):
                valid = False

        # Status
        if 'status' in rule:
            self.validate_status(rule['status'])

        # Logsource
        if 'logsource' in rule:
            if not self.validate_logsource(rule['logsource']):
                valid = False

        # Detection
        if 'detection' in rule:
            if not self.validate_detection(rule['detection']):
                valid = False

        # Tags
        if 'tags' in rule:
            self.validate_tags(rule['tags'])

        # Warnings for missing optional fields
        if 'author' not in rule:
            self.warnings.append("Consider adding 'author' field")

        if 'references' not in rule:
            self.warnings.append("Consider adding 'references' field")

        if 'falsepositives' not in rule:
            self.warnings.append("Consider adding 'falsepositives' field")

        if 'date' not in rule:
            self.warnings.append("Consider adding 'date' field")

        return valid

    def validate_file(self, file_path: Path) -> bool:
        """Validate a Sigma rule file."""
        self.errors = []
        self.warnings = []

        print(f"Validating: {file_path}")

        # Check YAML syntax
        syntax_valid, rule = self.validate_yaml_syntax(file_path)
        if not syntax_valid:
            return False

        # Validate rule structure
        rule_valid = self.validate_rule(rule)

        # Print results
        if self.errors:
            print("  ✗ ERRORS:")
            for error in self.errors:
                print(f"    - {error}")

        if self.warnings:
            print("  ⚠ WARNINGS:")
            for warning in self.warnings:
                print(f"    - {warning}")

        if rule_valid and not self.errors:
            print("  ✓ VALID")
            return True
        else:
            return False


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description='Validate Sigma detection rules'
    )
    parser.add_argument(
        'input',
        type=Path,
        help='Path to Sigma rule file or directory'
    )
    parser.add_argument(
        '--strict',
        action='store_true',
        help='Treat warnings as errors'
    )

    args = parser.parse_args()

    validator = SigmaValidator()

    # Process input
    if args.input.is_file():
        # Single file
        valid = validator.validate_file(args.input)
        if args.strict and validator.warnings:
            valid = False
        sys.exit(0 if valid else 1)

    elif args.input.is_dir():
        # Directory - process all .yml files
        sigma_files = list(args.input.rglob('*.yml')) + list(args.input.rglob('*.yaml'))

        if not sigma_files:
            print(f"No Sigma rule files found in {args.input}", file=sys.stderr)
            sys.exit(1)

        print(f"Validating {len(sigma_files)} Sigma rule(s)\n")

        valid_count = 0
        for sigma_file in sigma_files:
            if validator.validate_file(sigma_file):
                valid_count += 1
            print()  # Blank line between files

        print(f"Results: {valid_count}/{len(sigma_files)} valid")

        if args.strict:
            # Count files with warnings
            files_with_warnings = len(sigma_files) - valid_count
            if files_with_warnings > 0:
                sys.exit(1)

        sys.exit(0 if valid_count == len(sigma_files) else 1)

    else:
        print(f"Error: {args.input} is not a valid file or directory", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
