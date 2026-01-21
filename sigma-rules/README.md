# Sigma Detection Rules

This directory contains Sigma detection rules organized by platform/category.

## Directory Structure

- `windows/` - Windows-specific detections (Event Logs, Sysmon, etc.)
- `linux/` - Linux-specific detections (auditd, syslog, etc.)
- `cloud/` - Cloud platform detections (AWS, Azure, GCP)
- `network/` - Network-based detections (firewall, proxy, DNS)

## Sigma Rule Format

Each detection rule should follow the Sigma specification format:

```yaml
title: Detection Name
id: unique-uuid
status: experimental|test|stable
description: Brief description of what this detects
references:
    - https://reference-url.com
author: Your Name
date: YYYY-MM-DD
modified: YYYY-MM-DD
tags:
    - attack.tactic_name
    - attack.technique_id
logsource:
    category: category_name
    product: product_name
detection:
    selection:
        field: value
    condition: selection
falsepositives:
    - Known false positive scenarios
level: low|medium|high|critical
```

## Conversion Pipeline

1. **Sigma Rule** (`.yml`) - Platform-agnostic detection logic
2. **Sigma Converter** - Converts Sigma to Sumo Logic query format
3. **Terraform Module** - Deploys as Sumo Logic monitor
4. **Validation** - Tests query syntax and logic

## Adding New Detections

New detections are created by providing a use case description. The pipeline will:
1. Generate a Sigma rule based on the use case
2. Validate the Sigma syntax
3. Convert to Sumo Logic query format
4. Generate Terraform configuration
5. Deploy via GitHub Actions
