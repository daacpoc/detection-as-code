# Detection-as-Code Pipeline for Sumo Logic

A comprehensive detection engineering pipeline that converts Sigma detection rules to Sumo Logic queries and deploys them via Terraform.

## 🏗️ Architecture

```
┌─────────────────┐
│  Sigma Rules    │  Platform-agnostic detection logic
│   (.yml files)  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Validation    │  Syntax & schema validation
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Conversion    │  Sigma → Sumo Logic query
│  (Python script)│
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│   Terraform     │  Sumo Logic monitor resources
│  Configuration  │
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  GitHub Actions │  CI/CD automation
└────────┬────────┘
         │
         ↓
┌─────────────────┐
│  Sumo Logic     │  Deployed monitors
│    Platform     │
└─────────────────┘
```

## 📁 Repository Structure

```
detection-as-code/
├── sigma-rules/               # Sigma detection rules
│   ├── windows/              # Windows-specific detections
│   ├── linux/                # Linux-specific detections
│   ├── cloud/                # Cloud platform detections
│   └── network/              # Network-based detections
│
├── scripts/                   # Automation scripts
│   ├── converters/
│   │   └── sigma_to_sumologic.py   # Sigma → Sumo Logic converter
│   └── validators/
│       └── validate_sigma.py       # Sigma rule validator
│
├── detections/                # Generated Terraform configurations
│   └── tf-{detection-name}/  # One directory per detection
│       ├── {detection}.tf    # Terraform config
│       └── metadata.json     # Detection metadata
│
├── .github/
│   └── workflows/
│       └── detection-pipeline.yml  # CI/CD pipeline
│
├── main.tf                    # Root Terraform configuration
├── prompt.md                  # AI assistant instructions
└── README.md                  # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Terraform 1.0+
- Sumo Logic account with API credentials
- GitHub repository with Actions enabled

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd detection-as-code
   ```

2. **Configure Sumo Logic credentials**

   Add these secrets to your GitHub repository:
   - `TF_VAR_SUMOLOGIC_ACCESS_ID`
   - `TF_VAR_SUMOLOGIC_ACCESS_KEY`

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize Terraform**
   ```bash
   terraform init
   ```

## 📝 Creating New Detections

### Method 1: Manual Sigma Rule Creation

1. Create a new Sigma rule in the appropriate directory:
   ```bash
   touch sigma-rules/windows/my-detection.yml
   ```

2. Write your Sigma rule following the format in `prompt.md`

3. Commit and push:
   ```bash
   git add sigma-rules/windows/my-detection.yml
   git commit -m "Add detection for X"
   git push
   ```

4. The pipeline will automatically:
   - Validate the Sigma rule
   - Convert to Sumo Logic query
   - Generate Terraform configuration
   - Deploy to Sumo Logic (on main branch)

### Method 2: Using AI Assistant

Ask the AI assistant (configured with `prompt.md`) to create a detection:

```
"Create a detection for PowerShell execution with encoded commands"
```

The assistant will:
1. Generate a complete Sigma rule
2. Provide Sumo Logic query preview
3. Give confidence rating
4. Explain any considerations

Then save the generated rule to the appropriate directory.

## 🔄 Pipeline Workflow

### On Pull Request
1. **Validate** - Check Sigma rule syntax and schema
2. **Convert** - Generate Sumo Logic queries
3. **Plan** - Show Terraform changes

### On Merge to Main
1. **Validate** - Ensure rules are correct
2. **Convert** - Generate Terraform configs
3. **Plan** - Preview infrastructure changes
4. **Apply** - Deploy to Sumo Logic

## 🛠️ Scripts

### Validate Sigma Rules
```bash
python scripts/validators/validate_sigma.py sigma-rules/
```

Options:
- `--strict` - Treat warnings as errors

### Convert Sigma to Sumo Logic
```bash
python scripts/converters/sigma_to_sumologic.py sigma-rules/ --output-dir detections/
```

### Manual Terraform Deployment
```bash
terraform init
terraform plan
terraform apply
```

## 📋 Sigma Rule Template

```yaml
title: Detection Title
id: unique-uuid-here
status: experimental
description: |
  Detailed description of what this detects
references:
    - https://attack.mitre.org/techniques/TXXXX/
author: Your Name
date: 2025-01-21
tags:
    - attack.tactic
    - attack.tXXXX
logsource:
    product: windows
    category: security
detection:
    selection:
        EventID: XXXX
        Field: value
    condition: selection
falsepositives:
    - Known false positive scenarios
level: medium
```

## 🎯 Detection Categories

### Windows
- Process execution
- User account management
- Privilege escalation
- Lateral movement
- Persistence mechanisms

### Linux
- Process execution
- User/group modifications
- Scheduled tasks
- File system changes

### Cloud (AWS/Azure/GCP)
- IAM changes
- Resource creation/deletion
- Configuration changes
- Abnormal API calls

### Network
- DNS queries
- Proxy/web traffic
- Firewall events

## 🔍 Field Mappings

### Windows Event Logs → Sumo Logic

| Sigma Field | Sumo Logic Field |
|------------|------------------|
| EventID | eventid |
| Provider_Name | %"provider.name" |
| Channel | _sourceName |
| Computer | _sourceHost |
| CommandLine | commandline |
| Image | image |
| TargetUserName | %"event.user.name" |

### Common Source Filters

| Log Source | Sumo Logic Filter |
|-----------|------------------|
| Windows Security | _sourceName=Security |
| Sysmon | _sourceName=Sysmon |
| AWS CloudTrail | _sourceName=aws/cloudtrail |

## 🧪 Testing

### Local Validation
```bash
# Validate all rules
python scripts/validators/validate_sigma.py sigma-rules/

# Validate specific rule
python scripts/validators/validate_sigma.py sigma-rules/windows/my-rule.yml
```

### Local Conversion
```bash
# Convert all rules
python scripts/converters/sigma_to_sumologic.py sigma-rules/

# Convert specific rule
python scripts/converters/sigma_to_sumologic.py sigma-rules/windows/my-rule.yml
```

### Terraform Testing
```bash
# Format check
terraform fmt -check -recursive

# Validate configuration
terraform validate

# Plan without applying
terraform plan
```

## 📊 Monitoring

After deployment, monitors will be available in Sumo Logic under:
- **Library** → **Monitors**
- Tagged with: `ttp`, `logsource`, `owner`, `level`

## 🤝 Contributing

1. Create a feature branch
2. Add/modify Sigma rules
3. Ensure validation passes locally
4. Open a pull request
5. Review Terraform plan
6. Merge to deploy

## 🔐 Security Considerations

- API credentials stored as GitHub secrets
- Terraform state management recommended
- Review all detections before deploying to production
- Test in non-production environment first
- Monitor false positive rates

## 📚 Additional Resources

- [Sigma Specification](https://github.com/SigmaHQ/sigma-specification)
- [Sumo Logic Documentation](https://help.sumologic.com/)
- [Sumo Logic Terraform Provider](https://registry.terraform.io/providers/SumoLogic/sumologic/latest/docs)
- [MITRE ATT&CK Framework](https://attack.mitre.org/)

## 🐛 Troubleshooting

### Validation Failures
- Check YAML syntax
- Ensure all required fields present
- Validate UUID format
- Check MITRE ATT&CK tag format

### Conversion Issues
- Verify field mappings
- Check logsource compatibility
- Review detection logic complexity

### Deployment Failures
- Verify Sumo Logic credentials
- Check Terraform state
- Review query syntax
- Validate monitor configuration

## 📝 License

See LICENSE file for details.

## 👥 Support

For questions or issues:
1. Check existing documentation
2. Review example rules
3. Open an issue in this repository
