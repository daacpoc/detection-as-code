# Splunk app for storing detection rules as saved searches
# Docs: https://registry.terraform.io/providers/splunk/splunk/latest/docs/resources/apps_local

resource "splunk_apps_local" "detections" {
  name     = "detection_as_code"
  filename = false
  explicit_appname = "detection_as_code"

  # Metadata
  label       = "Detection as Code"
  description = "Security detection rules deployed via Terraform"
  version     = "1.0.0"
  author      = "Security Team"

  # Visibility
  visible = true
}
