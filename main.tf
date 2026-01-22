#Define variables here first to be passed to sub modules
variable "SUMOLOGIC_ACCESS_ID" {
  type        = string
  description = "Sumo Logic Access ID"
  sensitive   = true
}

variable "SUMOLOGIC_ACCESS_KEY" {
  type        = string
  description = "Sumo Logic Access Key"
  sensitive   = true
}

variable "SUMOLOGIC_ENVIRONMENT" {
  type        = string
  description = "Sumo Logic Environment (us1, us2, eu, etc.)"
  default     = "us1"
}

# Terraform configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    sumologic = {
      source  = "SumoLogic/sumologic"
      version = "~> 2.31"
    }
  }
}

# Configure the Sumo Logic Provider at root level
provider "sumologic" {
  access_id   = var.SUMOLOGIC_ACCESS_ID
  access_key  = var.SUMOLOGIC_ACCESS_KEY
  environment = var.SUMOLOGIC_ENVIRONMENT
}

#
# Detection Modules
# These are auto-generated from Sigma rules via the detection pipeline
# To add new detections, create Sigma rules in sigma-rules/ directory
#

# Existing manual detections (will be migrated to Sigma format)
module "tf-logs-monitor" {
  source = "./detections/tf-logs-monitor/"
}

module "tf-winevent-new-useradded" {
  source = "./detections/tf-winevent-new-useradded/"
}

# Future Sigma-generated detections will be automatically added here by the pipeline
# Example:
# module "example_user_creation" {
#   source = "./detections/tf-example_user_creation/"
# }