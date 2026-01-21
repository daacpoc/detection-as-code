# Detection-as-Code Pipeline Overview

## 🎯 Purpose

This pipeline mirrors the architecture shown in your reference image, but adapted for Sumo Logic instead of Splunk. It provides an end-to-end automated detection engineering workflow.

## 🏗️ Pipeline Architecture

### Pipeline Flow

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         DETECTION CREATION                                │
│                                                                            │
│  User Request  →  AI Assistant  →  Sigma Rule (YAML)                     │
│                  (prompt.md)                                               │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                         VALIDATION LAYER                                  │
│                                                                            │
│  ┌─────────────────┐                                                      │
│  │ validate_sigma  │  • YAML syntax check                                 │
│  │     .py         │  • Required fields verification                      │
│  └─────────────────┘  • UUID format validation                            │
│                       • MITRE ATT&CK tag validation                       │
│                       • Schema compliance                                 │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                       CONVERSION LAYER                                    │
│                                                                            │
│  ┌──────────────────────┐                                                 │
│  │ sigma_to_sumologic   │  • Field mapping (Sigma → Sumo Logic)           │
│  │       .py            │  • Query generation                             │
│  └──────────────────────┘  • Logsource translation                        │
│                            • Monitor configuration                        │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                    TERRAFORM GENERATION                                   │
│                                                                            │
│  ┌────────────────┐                                                       │
│  │  Terraform     │  • sumologic_monitor resource                         │
│  │  Config (.tf)  │  • Tags (TTP, logsource, owner)                       │
│  └────────────────┘  • Alert thresholds                                   │
│                      • Notification configuration                         │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                         CI/CD PIPELINE                                    │
│                      (GitHub Actions)                                     │
│                                                                            │
│  PR: Validate → Convert → Plan (show changes)                             │
│                                                                            │
│  Main: Validate → Convert → Plan → Apply (deploy)                         │
│                                                                            │
└──────────────────────────┬───────────────────────────────────────────────┘
                           │
                           ↓
┌──────────────────────────────────────────────────────────────────────────┐
│                       SUMO LOGIC PLATFORM                                 │
│                                                                            │
│  • Monitors deployed and active                                           │
│  • Alerts sent to configured recipients                                   │
│  • Tagged for organization (TTP, logsource, owner)                        │
│                                                                            │
└──────────────────────────────────────────────────────────────────────────┘
```

## 📊 Comparison with Reference Image

### Your Reference (Splunk-based)
1. Sigma Rule Generation
2. Detection Rule Generator Agent (using OpenAI API)
3. SPL Validation
4. Attack Test (Atomic Red Team)
5. Detect Test (Splunk)
6. Sigma to SPL Conversion
7. Documentation Creation

### Your New Pipeline (Sumo Logic-based)
1. ✅ Sigma Rule Generation (AI-assisted via prompt.md)
2. ✅ Validation (Python script - validate_sigma.py)
3. ✅ Conversion (Sigma → Sumo Logic - sigma_to_sumologic.py)
4. ✅ Terraform Generation (Infrastructure as Code)
5. ✅ CI/CD Automation (GitHub Actions)
6. ✅ Deployment (Sumo Logic Platform)

**Differences:**
- **Instead of OpenAI API**: You use prompt.md to configure the AI assistant
- **Instead of SPL**: You use Sumo Logic Query Language
- **Instead of manual testing**: CI/CD pipeline validates and deploys
- **Added**: Terraform for infrastructure as code
- **Added**: Full GitHub Actions integration

## 🔄 Workflow Examples

### Example 1: Creating a New Detection

**Step 1: Request**
```
You: "Create a detection for suspicious PowerShell execution with encoded commands"
```

**Step 2: AI Generates Sigma Rule**
```yaml
title: Suspicious PowerShell Encoded Command Execution
id: f26c6093-6f14-4b12-800f-0fcb46f5ffd0
status: experimental
description: Detects PowerShell execution with encoded commands (-enc, -encodedcommand)
  which is commonly used by attackers to obfuscate malicious commands
references:
  - https://attack.mitre.org/techniques/T1059/001/
  - https://attack.mitre.org/techniques/T1027/
tags:
  - attack.execution
  - attack.t1059.001
  - attack.defense_evasion
  - attack.t1027
logsource:
  product: windows
  category: process_creation
detection:
  selection:
    Image|endswith: '\powershell.exe'
    CommandLine|contains:
      - ' -enc '
      - ' -encodedcommand '
      - ' -ec '
  condition: selection
falsepositives:
  - Legitimate administrative scripts
  - Software deployment tools
level: medium
```

**Step 3: Save to Repository**
```bash
# You save the rule
echo "[sigma rule content]" > sigma-rules/windows/powershell-encoded-execution.yml
git add sigma-rules/windows/powershell-encoded-execution.yml
git commit -m "Add detection for encoded PowerShell commands"
git push
```

**Step 4: Pipeline Executes (Automatic)**

```
GitHub Actions triggers:

Job 1: Validate
  ✓ YAML syntax valid
  ✓ Required fields present
  ✓ UUID format correct
  ✓ Schema compliant

Job 2: Convert
  ✓ Fields mapped to Sumo Logic
  ✓ Query generated:
    _sourceName=Sysmon | where image matches "*\\powershell.exe"
    | where commandline matches "*-enc*" OR commandline matches "*-encodedcommand*"
  ✓ Terraform config created

Job 3: Plan
  ✓ Terraform plan shows new monitor
  ✓ No conflicts

Job 4: Apply (on main branch)
  ✓ Monitor created in Sumo Logic
  ✓ Alerts configured
  ✓ Tags applied
```

**Step 5: Monitor Active in Sumo Logic**
- Monitor appears in Sumo Logic Library
- Tagged with: TTP: T1059.001, logsource: windows, owner: secops
- Alerts sent when triggered

### Example 2: AWS IAM Detection

**Request:**
```
"Detect when someone creates a new IAM user in AWS"
```

**Generated Sigma Rule:**
```yaml
title: AWS IAM User Creation
id: 8a4b2e91-6c3d-4f2a-9d8e-1b5c6a7d8e9f
status: stable
description: Detects creation of new IAM users in AWS
tags:
  - attack.persistence
  - attack.t1136.003
logsource:
  product: aws
  service: cloudtrail
detection:
  selection:
    eventName: 'CreateUser'
    eventSource: 'iam.amazonaws.com'
  condition: selection
level: medium
```

**Converted Sumo Logic Query:**
```
_sourceName=aws/cloudtrail
| where eventName = "CreateUser"
| where eventSource = "iam.amazonaws.com"
```

## 🎛️ Components Breakdown

### 1. Sigma Rules Directory (`sigma-rules/`)

**Purpose**: Store platform-agnostic detection rules

**Structure:**
```
sigma-rules/
├── windows/     # Windows Event Logs, Sysmon
├── linux/       # auditd, syslog
├── cloud/       # AWS, Azure, GCP
└── network/     # Firewall, proxy, DNS
```

**File Format:** YAML (Sigma specification)

### 2. Validation Script (`scripts/validators/validate_sigma.py`)

**Purpose**: Ensure Sigma rules are correctly formatted

**Checks:**
- YAML syntax
- Required fields (title, id, description, logsource, detection, level)
- UUID format
- MITRE ATT&CK tag format
- Detection logic structure
- Condition references

**Usage:**
```bash
python scripts/validators/validate_sigma.py sigma-rules/
```

### 3. Conversion Script (`scripts/converters/sigma_to_sumologic.py`)

**Purpose**: Convert Sigma rules to Sumo Logic format

**Functions:**
- Field name mapping (Sigma → Sumo Logic)
- Logsource translation
- Query syntax generation
- Terraform configuration creation
- Metadata extraction

**Field Mappings:**
| Sigma | Sumo Logic |
|-------|-----------|
| EventID | eventid |
| Provider_Name | %"provider.name" |
| Channel | _sourceName |
| Computer | _sourceHost |
| CommandLine | commandline |

**Usage:**
```bash
python scripts/converters/sigma_to_sumologic.py sigma-rules/ --output-dir detections/
```

### 4. Detection Modules (`detections/`)

**Purpose**: Terraform configurations for Sumo Logic monitors

**Auto-generated structure:**
```
detections/
└── tf-{rule-name}/
    ├── {rule-name}.tf    # Terraform configuration
    └── metadata.json     # Detection metadata
```

**Each .tf file contains:**
- Sumo Logic provider configuration
- sumologic_monitor resource
- Query definition
- Alert thresholds
- Notification settings
- Tags (TTP, logsource, owner)

### 5. GitHub Actions Workflow (`.github/workflows/detection-pipeline.yml`)

**Purpose**: Automate the entire pipeline

**On Pull Request:**
1. Validate Sigma rules
2. Convert to Sumo Logic
3. Generate Terraform plan
4. Comment plan on PR

**On Push to Main:**
1. Validate Sigma rules
2. Convert to Sumo Logic
3. Generate Terraform plan
4. Apply (deploy to Sumo Logic)
5. Report results

### 6. Root Terraform Config (`main.tf`)

**Purpose**: Orchestrate all detection modules

**Contents:**
- Provider configuration
- Variable definitions
- Module declarations for each detection

**Automatically updated** when new detections are added

## 🔐 Security & Best Practices

### Secrets Management
- Sumo Logic credentials stored as GitHub secrets
- Never commit credentials to repository
- Terraform state should be remote (recommended)

### Quality Gates
1. **Validation** - Rules must pass validation
2. **Conversion** - Must generate valid Sumo Logic queries
3. **Terraform** - Must pass `terraform validate`
4. **Manual Review** - PR review before merge

### Tagging Strategy
Every detection is tagged with:
- **TTP**: MITRE ATT&CK technique ID
- **logsource**: Data source (windows, aws, linux, etc.)
- **owner**: Team responsible (secops, cloudops, etc.)
- **level**: Severity (critical, high, medium, low)

### Monitoring
- Review alert volumes regularly
- Track false positive rates
- Update rules based on findings
- Document tuning decisions

## 📈 Scaling the Pipeline

### Adding New Data Sources

**Step 1**: Update field mappings in `sigma_to_sumologic.py`
```python
self.field_mappings = {
    # Add new source fields
    'NewSourceField': 'sumo_field_name',
}
```

**Step 2**: Add logsource mapping
```python
self.logsource_mappings = {
    'new_product': {
        'category': {'_sourceName': 'NewSource'}
    }
}
```

**Step 3**: Create Sigma rules for new source
```yaml
logsource:
  product: new_product
  category: category
```

### Adding Advanced Features

**Testing Framework**
- Add unit tests for converters
- Integration tests with sample data
- Performance testing for complex queries

**Documentation Generation**
- Auto-generate detection documentation
- Create detection coverage matrix
- MITRE ATT&CK coverage heatmap

**Metrics & Reporting**
- Alert volume dashboards
- Detection effectiveness metrics
- Coverage reporting

## 🎓 Learning Resources

### Sigma Resources
- [Sigma Specification](https://github.com/SigmaHQ/sigma-specification)
- [Sigma Rule Repository](https://github.com/SigmaHQ/sigma)
- [Sigma Converter Tool](https://github.com/SigmaHQ/sigma-cli)

### Sumo Logic Resources
- [Sumo Logic Documentation](https://help.sumologic.com/)
- [Search Query Language](https://help.sumologic.com/docs/search/)
- [Monitors](https://help.sumologic.com/docs/alerts/monitors/)
- [Terraform Provider](https://registry.terraform.io/providers/SumoLogic/sumologic/latest/docs)

### MITRE ATT&CK
- [ATT&CK Navigator](https://mitre-attack.github.io/attack-navigator/)
- [ATT&CK Matrix](https://attack.mitre.org/matrices/enterprise/)
- [Technique Descriptions](https://attack.mitre.org/techniques/enterprise/)

## 🚀 Next Steps

1. **Test the Example** - Run validation and conversion on example rule
2. **Request a Detection** - Ask AI to create your first custom rule
3. **Deploy to Test** - Push to a test branch first
4. **Review Results** - Check Sumo Logic for deployed monitor
5. **Iterate** - Tune based on alerts and feedback
6. **Scale** - Add more detections systematically

## 💡 Pro Tips

1. **Start Simple** - Begin with well-known detections
2. **Use Templates** - Reference existing rules
3. **Test Locally** - Validate before pushing
4. **Document Decisions** - Note why rules were created/tuned
5. **Monitor Performance** - Watch query execution times
6. **Collaborate** - Review rules with team members
7. **Stay Updated** - Follow Sigma rule updates
8. **Track Coverage** - Map to MITRE ATT&CK

---

**You're now ready to run a production-grade Detection-as-Code pipeline for Sumo Logic!**
