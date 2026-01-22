# splunk_saved_searches docs: https://registry.terraform.io/providers/splunk/splunk/latest/docs/resources/saved_searches

terraform {
  required_providers {
    splunk = {
      source  = "splunk/splunk"
      version = "~> 2.0"
    }
  }
  required_version = ">= 1.5.2"
}

# Splunk Saved Search (alert) resource
resource "splunk_saved_searches" "alert" {
  name         = var.standard_name
  search       = var.standard_query
  description  = var.standard_description
  disabled     = false
  is_scheduled = true
  is_visible   = true

  # App context - where the saved search will be stored
  acl {
    app    = var.app_name
    owner  = "admin"
    sharing = "app"
  }

  # Schedule configuration
  cron_schedule = var.cron_schedule

  # Alert configuration
  actions        = var.webhook_url != null ? "webhook" : ""
  alert_type     = "number of events"
  alert_comparator = "greater than"
  alert_threshold  = "0"
  alert_condition  = var.alert_condition

  # Time range for the search
  dispatch_earliest_time = var.earliest_time
  dispatch_latest_time   = var.latest_time

  # Webhook action configuration
  dynamic "action_webhook" {
    for_each = var.webhook_url != null ? [1] : []
    content {
      webhook_url = var.webhook_url
      webhook_param_url = var.webhook_url
    }
  }
}
