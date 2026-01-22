# Workflow Guide

## How to Add New Detections

The pipeline has been simplified to work with committed files. Here's the updated workflow:

### Step 1: Request Detection from AI

Ask the AI assistant to create a detection:
```
"Create a detection for [describe threat/behavior]"
```

The AI will provide:
- Complete Sigma YAML rule
- Sumo Logic query preview
- Confidence rating
- Deployment instructions

### Step 2: Save Sigma Rule

Save the generated Sigma rule to the appropriate directory:
```bash
# Example: Save to sigma-rules/windows/
cat > sigma-rules/windows/my-detection.yml << 'EOF'
[paste Sigma rule content]
EOF
```

### Step 3: Convert Locally (Optional but Recommended)

Run the converter locally to generate Terraform modules:
```bash
python scripts/converters/sigma_to_sumologic.py sigma-rules/ --output-dir detections/
```

This creates:
```
detections/
└── tf-my_detection/
    ├── my_detection.tf      # Terraform resource
    └── metadata.json         # Detection metadata
```

### Step 4: Update main.tf (If New Detection)

Add a module declaration for the new detection in `main.tf`:
```hcl
module "my-detection" {
  source = "./detections/tf-my_detection/"
}
```

### Step 5: Test Locally

Validate everything works:
```bash
# Validate Sigma rules
python scripts/validators/validate_sigma.py sigma-rules/

# Initialize Terraform
terraform init

# Validate Terraform configuration
terraform validate

# Preview deployment
terraform plan
```

### Step 6: Commit and Push

```bash
git add sigma-rules/windows/my-detection.yml
git add detections/tf-my_detection/
git add main.tf
git commit -m "Add detection for [description]"
git push
```

### Step 7: GitHub Actions Pipeline

The pipeline automatically:
1. ✅ Validates Sigma rules
2. ✅ Runs `terraform init`
3. ✅ Runs `terraform validate`
4. ✅ Runs `terraform plan`
5. ✅ Applies plan to deploy (on main branch)

---

## Simplified Architecture

### Old Workflow (HAD ISSUES)
```
Push → Validate Sigma → Convert in CI → Upload Artifacts → Download → Terraform
                                           ❌ This overwrote committed files
```

### New Workflow (WORKING)
```
Convert Locally → Commit → Push → Validate Sigma → Terraform Plan → Terraform Apply
                                                      ✅ Uses committed files
```

---

## Key Changes

### ✅ What Changed
- **No longer converts Sigma in CI/CD** - You convert locally and commit the results
- **No artifact upload/download** - Works directly with git-tracked files
- **Simplified pipeline** - Single validate-and-plan job
- **Faster execution** - Fewer steps, less complexity

### ✅ Why This Works Better
- **No file overwrites** - Committed detection modules stay as-is
- **Version control** - All Terraform configs are tracked in git
- **Debugging** - Easy to see exactly what will be deployed
- **Consistency** - What you test locally is what deploys

---

## Quick Reference

### Create Detection
```bash
# 1. Ask AI to generate Sigma rule
# 2. Save to sigma-rules/{category}/
cat > sigma-rules/windows/my-rule.yml << 'EOF'
[Sigma YAML content]
EOF

# 3. Validate
python scripts/validators/validate_sigma.py sigma-rules/windows/my-rule.yml

# 4. Convert
python scripts/converters/sigma_to_sumologic.py sigma-rules/windows/my-rule.yml

# 5. Add module to main.tf
echo 'module "my-rule" { source = "./detections/tf-my_rule/" }' >> main.tf

# 6. Test
terraform init && terraform validate && terraform plan

# 7. Deploy
git add . && git commit -m "Add my detection" && git push
```

### Update Existing Detection
```bash
# 1. Edit Sigma rule
vi sigma-rules/windows/existing-rule.yml

# 2. Re-convert
python scripts/converters/sigma_to_sumologic.py sigma-rules/windows/existing-rule.yml

# 3. Test
terraform plan

# 4. Deploy
git add . && git commit -m "Update detection" && git push
```

### Delete Detection
```bash
# 1. Remove Sigma rule
rm sigma-rules/windows/old-rule.yml

# 2. Remove detection module
rm -rf detections/tf-old_rule/

# 3. Remove module declaration from main.tf
vi main.tf  # Remove the module "old-rule" block

# 4. Deploy
git add . && git commit -m "Remove detection" && git push
```

---

## Pipeline Status

Check pipeline runs:
```
https://github.com/daacpoc/detection-as-code/actions
```

View deployed monitors in Sumo Logic:
- Navigate to: **Library** → **Monitors**
- Filter by tags: `owner:secops`, `logsource:windows`, etc.

---

## Troubleshooting

### Pipeline Fails

**Check the GitHub Actions logs:**
1. Go to Actions tab
2. Click failed workflow run
3. Expand failed job

**Common fixes:**
- Ensure `main.tf` has correct module declarations
- Verify detection modules have NO provider blocks
- Check Terraform files use underscores (not hyphens) in resource names
- Run `terraform validate` locally first

### Local Testing Fails

**Terraform Init Fails:**
```bash
# Clean and reinitialize
rm -rf .terraform .terraform.lock.hcl
terraform init
```

**Validation Fails:**
```bash
# Check Sigma rules
python scripts/validators/validate_sigma.py sigma-rules/

# Check Terraform
terraform validate
```

### Converter Issues

**Converter creates invalid Terraform:**
- Check the converter script `scripts/converters/sigma_to_sumologic.py`
- Ensure it's NOT generating provider/terraform/variable blocks
- Only resource blocks should be generated

---

## Best Practices

1. **Always test locally first** - Run `terraform plan` before pushing
2. **Use meaningful commit messages** - Describe what detection does
3. **Validate Sigma rules** - Run validator before converting
4. **Review generated Terraform** - Check query syntax and tags
5. **Monitor pipeline** - Watch GitHub Actions for errors
6. **Check Sumo Logic** - Verify monitors deploy correctly
7. **Document detections** - Add comments explaining detection logic
8. **Tag appropriately** - Use correct MITRE ATT&CK tags

---

## Example: Full Workflow

```bash
# 1. Request detection
# Ask AI: "Create a detection for SSH brute force attempts"

# 2. Save Sigma rule
cat > sigma-rules/linux/ssh-brute-force.yml << 'EOF'
title: SSH Brute Force Attempts
id: a1b2c3d4-e5f6-7890-abcd-ef1234567890
status: experimental
description: Detects multiple failed SSH login attempts
logsource:
  product: linux
  category: auth
detection:
  selection:
    EventType: 'Failed password'
    Service: 'ssh'
  condition: selection | count() by srcip > 5
level: high
tags:
  - attack.credential_access
  - attack.t1110
falsepositives:
  - Legitimate user password mistyping
EOF

# 3. Validate
python scripts/validators/validate_sigma.py sigma-rules/linux/ssh-brute-force.yml
# ✓ VALID

# 4. Convert
python scripts/converters/sigma_to_sumologic.py sigma-rules/linux/ssh-brute-force.yml
# ✓ Converted: ssh-brute-force.yml -> detections/tf-ssh_brute_force/ssh_brute_force.tf

# 5. Add to main.tf
cat >> main.tf << 'EOF'

module "ssh-brute-force" {
  source = "./detections/tf-ssh_brute_force/"
}
EOF

# 6. Test
terraform init
# Initializing modules...
# - ssh-brute-force in detections/tf-ssh_brute_force

terraform validate
# Success! The configuration is valid.

terraform plan
# Plan: 1 to add, 0 to change, 0 to destroy.

# 7. Commit and push
git add sigma-rules/linux/ssh-brute-force.yml
git add detections/tf-ssh_brute_force/
git add main.tf
git commit -m "Add detection for SSH brute force attempts"
git push

# 8. Monitor pipeline
# GitHub Actions runs:
#   ✓ Validate Sigma rules
#   ✓ Terraform Init
#   ✓ Terraform Validate
#   ✓ Terraform Plan
#   ✓ Terraform Apply (deploys to Sumo Logic)

# 9. Verify in Sumo Logic
# New monitor "SSH Brute Force Attempts" appears in Library
# Tagged: ttp=T1110, logsource=linux, owner=secops
```

---

## Summary

The pipeline now uses a **commit-first** approach:
1. Create Sigma rules
2. Convert locally
3. Commit everything
4. Pipeline validates and deploys committed files

This ensures what you test locally is exactly what gets deployed, with no surprises from CI/CD overwriting your files.
