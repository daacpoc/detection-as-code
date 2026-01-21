# Quick Start Guide

## 🎯 Your Detection-as-Code Pipeline is Ready!

This guide will help you start creating detections immediately.

## What You Can Do Now

### 1. Ask Me to Create Detections

Simply describe what you want to detect, and I'll create a Sigma rule for you:

**Examples:**
- "Create a detection for suspicious PowerShell execution"
- "Detect AWS root account usage"
- "Alert on failed SSH login attempts"
- "Find processes running from temp directories"
- "Detect lateral movement using PsExec"

### 2. How It Works

When you request a detection, I will:

1. **Generate Sigma Rule** - Create a platform-agnostic detection in YAML format
2. **Validate Compatibility** - Check if it works with Sumo Logic
3. **Provide Confidence Rating** - HIGH/MEDIUM/LOW/UNKNOWN
4. **Show Sumo Logic Query** - Converted query format
5. **Save to Repository** - Ready for deployment

### 3. Example Workflow

**You ask:**
```
"Create a detection for new Windows local user creation"
```

**I provide:**
- Complete Sigma YAML rule
- Sumo Logic query preview
- Deployment instructions
- Confidence rating

**You do:**
```bash
# Save the rule I created to sigma-rules/windows/
git add sigma-rules/windows/user-creation.yml
git commit -m "Add user creation detection"
git push
```

**Pipeline automatically:**
1. Validates the Sigma rule ✓
2. Converts to Sumo Logic format ✓
3. Generates Terraform configuration ✓
4. Deploys to your Sumo Logic instance ✓

## 📋 Current Structure

```
Your Repository
├── sigma-rules/          ← Put new detection rules here
│   ├── windows/         ← Windows detections
│   ├── linux/           ← Linux detections
│   ├── cloud/           ← Cloud (AWS/Azure/GCP)
│   └── network/         ← Network detections
│
├── scripts/
│   ├── converters/      ← Sigma → Sumo Logic converter
│   └── validators/      ← Rule validation
│
├── detections/          ← Auto-generated Terraform (DO NOT EDIT MANUALLY)
│
└── prompt.md            ← AI assistant configuration
```

## 🚀 Getting Started Right Now

### Option 1: Request a Detection

Just ask me:
```
"Create a detection for [describe the threat or behavior]"
```

### Option 2: Test the Example

I've created an example rule for you at:
`sigma-rules/windows/example-user-creation.yml`

Test the pipeline:
```bash
# Validate
python scripts/validators/validate_sigma.py sigma-rules/windows/example-user-creation.yml

# Convert
python scripts/converters/sigma_to_sumologic.py sigma-rules/windows/example-user-creation.yml --output-dir detections/

# Check output
ls detections/
```

### Option 3: Browse MITRE ATT&CK

Pick a technique from [MITRE ATT&CK](https://attack.mitre.org/) and ask me to create a detection for it:

```
"Create a detection for T1136.001 - Create Account: Local Account"
```

## 📝 What Detections Should You Create?

Think about:
- **Critical assets** - What systems are most important?
- **Known threats** - What attacks are you concerned about?
- **Compliance** - What monitoring is required?
- **Incident response** - What would help investigations?

### Common Starting Points

**Windows Security**
- User account creation/modification
- Privilege escalation attempts
- Suspicious process execution
- Credential dumping
- Lateral movement

**Cloud Security (AWS/Azure/GCP)**
- Root/admin account usage
- IAM policy changes
- Resource creation/deletion
- Unusual API calls
- Cross-account access

**Linux Security**
- Sudo usage
- SSH access patterns
- Cron job modifications
- Privilege escalation
- Unusual process execution

**Network Security**
- DNS exfiltration
- Unusual outbound connections
- Port scanning
- Protocol anomalies

## 🎓 Learning by Example

### Example 1: Request a Windows Detection

**You:**
```
"Create a detection for mimikatz credential dumping"
```

**I'll provide:**
- Sigma rule with proper fields
- MITRE ATT&CK tags (T1003)
- Sumo Logic query
- False positive considerations

### Example 2: Request a Cloud Detection

**You:**
```
"Detect when someone creates a new IAM user in AWS"
```

**I'll provide:**
- CloudTrail-based Sigma rule
- Appropriate AWS field mappings
- Sumo Logic CloudTrail query
- Alert threshold recommendations

## ⚙️ Pipeline Features

### Automatic Validation
- YAML syntax checking
- Required field verification
- UUID format validation
- MITRE ATT&CK tag validation

### Smart Conversion
- Field name mapping (Sigma → Sumo Logic)
- Query optimization
- Proper escaping for Sumo Logic syntax
- Tag preservation

### Terraform Generation
- Monitor resource creation
- Proper tagging (TTP, logsource, owner)
- Alert threshold configuration
- Email notification setup

### CI/CD Integration
- Validates on pull request
- Converts and plans deployment
- Auto-deploys to Sumo Logic on merge to main
- GitHub Actions status checks

## 🔧 Local Development

### Test Before Deploying

```bash
# 1. Validate your Sigma rule
python scripts/validators/validate_sigma.py sigma-rules/windows/my-rule.yml

# 2. Convert to Sumo Logic
python scripts/converters/sigma_to_sumologic.py sigma-rules/windows/my-rule.yml

# 3. Review generated Terraform
cat detections/tf-my-rule/my-rule.tf

# 4. Test Terraform
terraform init
terraform plan
```

## 🎯 Next Steps

1. **Think of a detection you need**
2. **Ask me to create it** (describe the threat/behavior)
3. **Review the Sigma rule I generate**
4. **Save it to the appropriate directory**
5. **Commit and push**
6. **Watch the pipeline deploy it**

## 💡 Tips

- **Be specific** - "Detect RDP brute force" is better than "Detect bad logins"
- **Mention the log source** - If you know it comes from Windows Security logs, say so
- **Include context** - "For SOC monitoring" vs "For compliance" helps me tune the rule
- **Ask questions** - I can explain any part of the detection logic

## 🆘 Need Help?

Just ask me:
- "Explain the Sigma rule format"
- "What fields are available in Sysmon logs?"
- "How do I reduce false positives?"
- "Show me examples of good detection rules"
- "What MITRE techniques should I prioritize?"

## 🎉 You're Ready!

Your detection-as-code pipeline is fully configured. Just ask me to create your first detection and we'll get started!

**Example to try right now:**
```
"Create a detection for PowerShell downloading files from the internet"
```

I'll generate a complete, production-ready Sigma rule that you can deploy immediately.
