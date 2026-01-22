#!/usr/bin/env python3
"""
Sigma to Sumo Logic Query Converter

This script converts Sigma detection rules to Sumo Logic query format.
It reads Sigma YAML files and generates Sumo Logic query syntax.
"""

import yaml
import json
import argparse
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional


class SigmaToSumoLogicConverter:
    """Converts Sigma rules to Sumo Logic query format."""

    def __init__(self):
        # Mapping of common Sigma fields to Sumo Logic fields
        self.field_mappings = {
            # Windows Event Log fields
            'EventID': 'eventid',
            'ProviderName': '%"provider.name"',
            'Provider_Name': '%"provider.name"',
            'Channel': '_sourceName',
            'Computer': '_sourceHost',
            'UserName': 'user',
            'User': 'user',
            'TargetUserName': '%"event.user.name"',
            'SubjectUserName': '%"event.subject.user.name"',
            'CommandLine': 'commandline',
            'Image': 'image',
            'ParentImage': 'parent_image',
            'ProcessId': 'process_id',
            'ParentProcessId': 'parent_process_id',
            'SourceIp': 'src_ip',
            'DestinationIp': 'dest_ip',
            'SourcePort': 'src_port',
            'DestinationPort': 'dest_port',
        }

        # Logsource mappings
        self.logsource_mappings = {
            'windows': {
                'security': {'_sourceName': 'Security'},
                'system': {'_sourceName': 'System'},
                'application': {'_sourceName': 'Application'},
                'sysmon': {'_sourceName': 'Sysmon'},
                'powershell': {'_sourceName': 'PowerShell'},
                'wmi': {'_sourceName': 'WMI'},
            },
            'linux': {
                'auditd': {'_sourceName': 'auditd'},
                'syslog': {'_sourceName': 'syslog'},
                'auth': {'_sourceName': 'auth'},
            },
            'cloud': {
                'aws': {'_sourceName': 'aws'},
                'azure': {'_sourceName': 'azure'},
                'gcp': {'_sourceName': 'gcp'},
            }
        }

    def convert_field_name(self, sigma_field: str) -> str:
        """Convert Sigma field name to Sumo Logic field name."""
        # Check direct mapping first
        if sigma_field in self.field_mappings:
            return self.field_mappings[sigma_field]

        # Convert camelCase to lowercase with underscores
        result = sigma_field.lower()
        return result

    def convert_value(self, value: Any) -> str:
        """Convert Sigma value to Sumo Logic query value."""
        if isinstance(value, str):
            # Handle wildcards
            if '*' in value:
                # Sumo Logic uses * for wildcard matching
                return f'"{value}"'
            # Regular string value
            return f'"{value}"'
        elif isinstance(value, int):
            return str(value)
        elif isinstance(value, list):
            # Handle list of values (OR condition)
            return ' OR '.join([self.convert_value(v) for v in value])
        return str(value)

    def build_selection_query(self, selection: Dict[str, Any]) -> str:
        """Build query from a selection dictionary."""
        conditions = []

        for field, value in selection.items():
            sumo_field = self.convert_field_name(field)

            if isinstance(value, list):
                # Multiple values = OR condition
                value_conditions = [f'{sumo_field} = {self.convert_value(v)}' for v in value]
                conditions.append(f'({" OR ".join(value_conditions)})')
            elif isinstance(value, dict):
                # Handle modifiers like 'contains', 'startswith', etc.
                if 'contains' in value:
                    conditions.append(f'{sumo_field} matches "*{value["contains"]}*"')
                elif 'startswith' in value:
                    conditions.append(f'{sumo_field} matches "{value["startswith"]}*"')
                elif 'endswith' in value:
                    conditions.append(f'{sumo_field} matches "*{value["endswith"]}"')
                else:
                    # Default to equality
                    conditions.append(f'{sumo_field} = {self.convert_value(value)}')
            else:
                # Simple equality
                conditions.append(f'{sumo_field} = {self.convert_value(value)}')

        return ' | where ' + ' AND '.join(conditions) if conditions else ''

    def get_logsource_filter(self, logsource: Dict[str, str]) -> str:
        """Generate Sumo Logic source filter from logsource."""
        filters = []

        product = logsource.get('product', '').lower()
        category = logsource.get('category', '').lower()
        service = logsource.get('service', '').lower()

        # Map logsource to Sumo Logic source filter
        if product in self.logsource_mappings:
            if category and category in self.logsource_mappings[product]:
                source_mapping = self.logsource_mappings[product][category]
                for key, value in source_mapping.items():
                    filters.append(f'{key}={value}')
            elif service and service in self.logsource_mappings[product]:
                source_mapping = self.logsource_mappings[product][service]
                for key, value in source_mapping.items():
                    filters.append(f'{key}={value}')

        return ' '.join(filters) if filters else '_index=*'

    def parse_condition(self, condition: str, detection: Dict[str, Any]) -> str:
        """Parse Sigma condition and build Sumo Logic query."""
        # This is a simplified condition parser
        # For complex conditions, you may need more sophisticated parsing

        # Handle simple conditions like "selection" or "selection and not filter"
        query_parts = []

        # Extract selection names from condition
        selections = []
        for key in detection.keys():
            if key != 'condition' and key in condition:
                selections.append(key)

        # Build query from selections
        for selection_name in selections:
            selection = detection[selection_name]
            if isinstance(selection, dict):
                query_parts.append(self.build_selection_query(selection))

        return ''.join(query_parts)

    def convert_sigma_to_sumologic(self, sigma_rule: Dict[str, Any]) -> Dict[str, Any]:
        """Convert a Sigma rule to Sumo Logic monitor configuration."""

        # Extract rule metadata
        title = sigma_rule.get('title', 'Untitled Detection')
        description = sigma_rule.get('description', '')
        level = sigma_rule.get('level', 'medium')
        tags = sigma_rule.get('tags', [])

        # Extract detection logic
        detection = sigma_rule.get('detection', {})
        logsource = sigma_rule.get('logsource', {})

        # Build base query from logsource
        base_query = self.get_logsource_filter(logsource)

        # Parse condition and build detection query
        condition = detection.get('condition', '')
        detection_query = self.parse_condition(condition, detection)

        # Combine queries
        full_query = base_query + detection_query

        # Extract MITRE ATT&CK tags
        mitre_tags = {}
        for tag in tags:
            if tag.startswith('attack.t'):
                mitre_tags['ttp'] = tag.replace('attack.', '').upper()
            elif tag.startswith('attack.'):
                tactic = tag.replace('attack.', '')
                mitre_tags.setdefault('tactic', []).append(tactic)

        # Determine logsource tag
        logsource_tag = logsource.get('product', 'generic')

        # Map severity level to alert threshold
        severity_map = {
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 1,
            'informational': 2
        }

        return {
            'name': title,
            'description': description,
            'query': full_query,
            'level': level,
            'tags': {
                'ttp': mitre_tags.get('ttp', ''),
                'logsource': logsource_tag,
                'owner': 'secops'
            },
            'threshold': severity_map.get(level, 0)
        }

    def generate_terraform(self, monitor_config: Dict[str, Any], rule_id: str) -> str:
        """Generate Terraform configuration for Sumo Logic monitor."""

        terraform_template = f'''# Sumo Logic Monitor Module
# Provider configuration is inherited from root main.tf
# This module only defines the monitor resource

resource "sumologic_monitor" "{rule_id}" {{
  name                      = "{monitor_config['name']}"
  description               = "{monitor_config['description']}"
  type                      = "MonitorsLibraryMonitor"
  is_disabled               = false
  monitor_type              = "Logs"
  evaluation_delay          = "0m"
  notification_group_fields = ["_sourcehost"]

  tags = {{
    "ttp"       = "{monitor_config['tags'].get('ttp', '')}"
    "logsource" = "{monitor_config['tags'].get('logsource', '')}"
    "owner"     = "{monitor_config['tags'].get('owner', 'secops')}"
    "level"     = "{monitor_config['level']}"
  }}

  queries {{
    row_id = "A"
    query  = "{monitor_config['query']}"
  }}

  trigger_conditions {{
    logs_static_condition {{
      warning {{
        time_range = "-15m"
        alert {{
          threshold      = {monitor_config['threshold']}
          threshold_type = "GreaterThan"
        }}
        resolution {{
          threshold         = {monitor_config['threshold']}
          threshold_type    = "LessThanOrEqual"
          resolution_window = "15m"
        }}
      }}
    }}
  }}

  notifications {{
    notification {{
      connection_type = "Email"
      recipients = [
        "secops@example.com",
      ]
      subject      = "Monitor Alert: {{{{TriggerType}}}} on {{{{Name}}}}"
      time_zone    = "UTC"
      message_body = "Triggered {{{{TriggerType}}}} Alert on {{{{Name}}}}: {{{{QueryURL}}}}"
    }}
    run_for_trigger_types = ["Warning"]
  }}
}}
'''
        return terraform_template

    def convert_file(self, sigma_file: Path, output_dir: Path) -> bool:
        """Convert a Sigma rule file to Sumo Logic Terraform configuration."""
        try:
            # Read Sigma rule
            with open(sigma_file, 'r', encoding='utf-8') as f:
                sigma_rule = yaml.safe_load(f)

            # Convert to Sumo Logic format
            monitor_config = self.convert_sigma_to_sumologic(sigma_rule)

            # Generate rule ID from filename
            rule_id = sigma_file.stem.replace('-', '_').replace(' ', '_')

            # Generate Terraform configuration
            terraform_config = self.generate_terraform(monitor_config, rule_id)

            # Create output directory
            detection_dir = output_dir / f"tf-{rule_id}"
            detection_dir.mkdir(parents=True, exist_ok=True)

            # Write Terraform file
            tf_file = detection_dir / f"{rule_id}.tf"
            with open(tf_file, 'w', encoding='utf-8') as f:
                f.write(terraform_config)

            # Write metadata JSON
            metadata_file = detection_dir / "metadata.json"
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(monitor_config, f, indent=2)

            print(f"✓ Converted: {sigma_file.name} -> {tf_file}")
            return True

        except Exception as e:
            print(f"✗ Error converting {sigma_file.name}: {str(e)}", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(
        description='Convert Sigma detection rules to Sumo Logic Terraform configurations'
    )
    parser.add_argument(
        'input',
        type=Path,
        help='Path to Sigma rule file or directory'
    )
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('./detections'),
        help='Output directory for Terraform configurations (default: ./detections)'
    )

    args = parser.parse_args()

    converter = SigmaToSumoLogicConverter()

    # Process input
    if args.input.is_file():
        # Single file
        success = converter.convert_file(args.input, args.output_dir)
        sys.exit(0 if success else 1)
    elif args.input.is_dir():
        # Directory - process all .yml files
        sigma_files = list(args.input.rglob('*.yml')) + list(args.input.rglob('*.yaml'))

        if not sigma_files:
            print(f"No Sigma rule files found in {args.input}", file=sys.stderr)
            sys.exit(1)

        print(f"Found {len(sigma_files)} Sigma rule(s)")

        success_count = 0
        for sigma_file in sigma_files:
            if converter.convert_file(sigma_file, args.output_dir):
                success_count += 1

        print(f"\nConverted {success_count}/{len(sigma_files)} rule(s)")
        sys.exit(0 if success_count == len(sigma_files) else 1)
    else:
        print(f"Error: {args.input} is not a valid file or directory", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
