# Sigma Detection Rules

This directory contains detection rules written in [Sigma](https://github.com/SigmaHQ/sigma) format. Sigma is a generic signature format for SIEM systems that allows you to write detection rules once and convert them to multiple backend formats.

## Why Sigma?

- **Portability**: Write rules once, deploy to multiple SIEM platforms (Splunk, Elastic, QRadar, etc.)
- **Standard Format**: Industry-standard YAML-based rule format
- **Version Control Friendly**: Text-based format works well with Git
- **Community**: Large library of pre-built rules from the Sigma community

## How It Works

1. **Write Rules**: Create detection rules in Sigma YAML format in this directory
2. **CI/CD Conversion**: The GitHub Actions workflow automatically converts Sigma rules to Splunk SPL queries using sigma-cli
3. **Terraform Deployment**: Converted queries are deployed to Splunk Cloud as saved searches via Terraform

## Rule Format

Example Sigma rule structure:

```yaml
title: Rule Name
id: unique-uuid-here
status: experimental|testing|production
description: What this rule detects
references:
    - https://link-to-documentation
author: Your Name
date: 2024/01/01
modified: 2024/01/01
tags:
    - attack.privilege_escalation
    - attack.t1078
logsource:
    product: okta
    service: okta
detection:
    selection:
        eventType: suspicious.event
    filter:
        user|startswith: 'admin.'
    condition: selection and not filter
falsepositives:
    - Legitimate activity description
level: high|medium|low
```

## Adding New Rules

1. Create a new `.yml` or `.yaml` file in this directory
2. Follow the Sigma rule format (see example above)
3. Commit and push your changes
4. The CI/CD pipeline will automatically convert and deploy the rule

## Local Testing

To test rule conversion locally:

```bash
# Install dependencies
pip install -r requirements.txt

# Convert rules
python convert_sigma_rules.py

# Check the output
cat converted_rules.json
```

## Resources

- [Sigma Specification](https://github.com/SigmaHQ/sigma-specification)
- [Sigma Rule Repository](https://github.com/SigmaHQ/sigma)
- [Sigconverter.io](https://sigconverter.io/)
- [pySigma Documentation](https://github.com/SigmaHQ/pySigma)
