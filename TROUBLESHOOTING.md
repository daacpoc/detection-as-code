# Troubleshooting Guide

## Common Issues and Solutions

### Issue 1: "Duplicate required providers configuration" Error

**Error Message:**
```
Error: Duplicate required providers configuration
  on detections/tf-winevent-new-useradded/tf-winevent-new-useradded.tf line 3
A module may have only one required providers configuration.
```

**Root Cause:**
- Detection module files contained their own `terraform {}`, `provider {}`, and `variable {}` blocks
- These should only exist at the root `main.tf` level
- Terraform modules inherit provider configuration from the root

**Solution (FIXED in commit 8b82954):**
1. Removed provider configuration from all detection module files
2. Updated converter script to generate clean module files
3. Provider is now only configured in root `main.tf`
4. Modules no longer receive variables - they inherit provider directly

**Before (WRONG):**
```hcl
# detections/tf-my-detection/my-detection.tf
terraform {
  required_providers {
    sumologic = { ... }
  }
}

variable "SUMOLOGIC_ACCESS_ID" { ... }
variable "SUMOLOGIC_ACCESS_KEY" { ... }

provider "sumologic" {
  access_id = var.SUMOLOGIC_ACCESS_ID
  ...
}

resource "sumologic_monitor" "my_detection" { ... }
```

**After (CORRECT):**
```hcl
# detections/tf-my-detection/my-detection.tf
# Sumo Logic Monitor Module
# Provider configuration is inherited from root main.tf

resource "sumologic_monitor" "my_detection" { ... }
```

**Root main.tf (CORRECT):**
```hcl
# main.tf
terraform {
  required_providers {
    sumologic = { ... }
  }
}

provider "sumologic" {
  access_id   = var.SUMOLOGIC_ACCESS_ID
  access_key  = var.SUMOLOGIC_ACCESS_KEY
  environment = var.SUMOLOGIC_ENVIRONMENT
}

module "my-detection" {
  source = "./detections/tf-my-detection/"
  # No variables needed - provider is inherited
}
```

---

### Issue 2: Multiple .tf Files in Same Module Directory

**Problem:**
Having multiple Terraform files in the same module directory that both define providers/variables causes conflicts.

**Example:**
```
detections/tf-winevent-new-useradded/
├── test-alert.tf              # Has provider block
└── tf-winevent-new-useradded.tf  # Also has provider block ❌
```

**Solutions:**

**Option 1: Combine into one file**
```bash
# Merge both resources into a single file
cat test-alert.tf tf-winevent-new-useradded.tf > combined.tf
# Then remove duplicate provider blocks
```

**Option 2: Separate module directories**
```bash
# Create separate directories for each detection
detections/
├── tf-test-alert/
│   └── test-alert.tf
└── tf-winevent-new-useradded/
    └── tf-winevent-new-useradded.tf
```

**Option 3: Remove provider blocks from all files (RECOMMENDED)**
This is what we did - all files in the same directory can coexist as long as they only contain resources.

---

### Issue 3: Resource Name Validation Errors

**Problem:**
Terraform resource names should use underscores, not hyphens.

**Wrong:**
```hcl
resource "sumologic_monitor" "tf-my-detection" {  # ❌ hyphens
```

**Correct:**
```hcl
resource "sumologic_monitor" "tf_my_detection" {  # ✓ underscores
```

---

### Issue 4: GitHub Actions Pipeline Fails on Terraform Init

**Symptoms:**
- Pipeline fails at "Terraform Init" step
- Error about duplicate configurations

**Solution:**
1. Check that all module files only contain resources
2. Verify root `main.tf` has single provider configuration
3. Ensure modules don't declare their own variables/providers

**Debug locally:**
```bash
# Clean up any cached files
rm -rf .terraform
rm -f .terraform.lock.hcl

# Re-initialize
terraform init

# Check for errors
terraform validate
```

---

### Issue 5: Sigma Conversion Creates Invalid Terraform

**Problem:**
Converter script generates modules with provider blocks.

**Fix:**
Update `scripts/converters/sigma_to_sumologic.py` to generate clean modules:

```python
def generate_terraform(self, monitor_config: Dict[str, Any], rule_id: str) -> str:
    terraform_template = f'''# Sumo Logic Monitor Module
# Provider configuration is inherited from root main.tf

resource "sumologic_monitor" "{rule_id}" {{
    # ... resource configuration ...
}}
'''
```

---

## Validation Checklist

Before pushing changes, verify:

- [ ] Root `main.tf` has single provider configuration
- [ ] Detection module files contain ONLY resources
- [ ] No duplicate terraform/provider/variable blocks
- [ ] Resource names use underscores, not hyphens
- [ ] All module declarations in main.tf use only `source` parameter
- [ ] Run `terraform init` locally without errors
- [ ] Run `terraform validate` successfully
- [ ] Run `terraform plan` to preview changes

---

## Testing Locally

### 1. Clean Environment
```bash
cd /path/to/detection-as-code
rm -rf .terraform .terraform.lock.hcl
```

### 2. Validate Sigma Rules
```bash
python scripts/validators/validate_sigma.py sigma-rules/
```

### 3. Convert Sigma to Sumo Logic
```bash
python scripts/converters/sigma_to_sumologic.py sigma-rules/ --output-dir detections/
```

### 4. Check Generated Files
```bash
# Ensure no provider blocks in module files
grep -r "provider \"sumologic\"" detections/
# Should only appear in main.tf

# Ensure no variable blocks in module files
grep -r "^variable" detections/
# Should only appear in main.tf
```

### 5. Terraform Validation
```bash
terraform init
terraform validate
terraform fmt -check -recursive
terraform plan
```

---

## GitHub Actions Debugging

### View Pipeline Logs
1. Go to: https://github.com/daacpoc/detection-as-code/actions
2. Click on the failing workflow run
3. Expand the failed job
4. Review error messages

### Common Pipeline Errors

**Error: "Terraform exited with code 1"**
- Usually indicates configuration errors
- Check "Terraform Init" or "Terraform Validate" step output
- Look for duplicate provider/variable errors

**Error: "No Sigma rule files found"**
- Sigma rules not in expected location
- Check `sigma-rules/` directory structure
- Verify `.yml` or `.yaml` file extensions

**Error: "Validation failed"**
- Sigma rule has syntax errors
- Missing required fields
- Invalid UUID format
- Run validator locally first

---

## Emergency Rollback

If the pipeline breaks after a commit:

```bash
# View recent commits
git log --oneline -5

# Revert to previous working commit
git revert HEAD

# Or reset to specific commit (use with caution)
git reset --hard <commit-hash>
git push --force origin main
```

---

## Getting Help

1. **Check this troubleshooting guide first**
2. **Review GitHub Actions logs** for specific errors
3. **Test locally** using validation checklist above
4. **Check recent commits** for what changed
5. **Ask for assistance** with specific error messages

---

## Preventive Measures

To avoid common issues:

1. **Always test locally** before pushing
2. **Use the converter script** instead of manual Terraform files
3. **Follow the established pattern** for new detections
4. **Keep root main.tf clean** - only provider config and modules
5. **Use Sigma rules** as the source of truth
6. **Let the pipeline generate** Terraform configs

---

## Current Working Configuration

As of commit `8b82954`, the pipeline uses this structure:

**Root Level (`main.tf`):**
- Single `terraform {}` block
- Single `provider "sumologic" {}` block
- Variable definitions for credentials
- Module declarations (source only)

**Detection Modules:**
- Only contain `resource` blocks
- No provider/terraform/variable blocks
- Inherit provider from root
- One or more resources per module

**Converter Output:**
- Generates clean module files
- Only resource definitions
- Proper field escaping
- Correct tag structure

This configuration has been tested and works correctly with GitHub Actions.
