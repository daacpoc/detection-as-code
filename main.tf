terraform {
  required_providers {
    # Splunk Provider docs: https://registry.terraform.io/providers/splunk/splunk/latest/docs
    splunk = {
      source  = "splunk/splunk"
      version = "~> 2.0"
    }
  }
  # Required Terraform version.
  required_version = ">= 1.5.2"
}

# Setup authentication variables. Docs: https://registry.terraform.io/providers/splunk/splunk/latest/docs
variable "SPLUNK_URL" {
  type        = string
  description = "Splunk Cloud instance URL (e.g., https://your-instance.splunkcloud.com:8089)"
}

variable "SPLUNK_USERNAME" {
  type        = string
  description = "Splunk admin username"
  default     = "admin"
}

variable "SPLUNK_PASSWORD" {
  type        = string
  description = "Splunk admin password"
  sensitive   = true
}

# Configure the Splunk Provider
provider "splunk" {
  url                  = var.SPLUNK_URL
  username             = var.SPLUNK_USERNAME
  password             = var.SPLUNK_PASSWORD
  insecure_skip_verify = false
}
