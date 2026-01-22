variable "standard_name" {
  type        = string
  description = "Name of the saved search/alert"
}

variable "standard_description" {
  type        = string
  description = "Description of what this alert detects"
}

variable "standard_query" {
  type        = string
  description = "Splunk SPL (Search Processing Language) query"
}

variable "app_name" {
  type        = string
  description = "Splunk app name where the saved search will be stored"
  default     = "detection_as_code"
}

variable "cron_schedule" {
  type        = string
  description = "Cron schedule for running the search"
  default     = "*/5 * * * *" # Every 5 minutes
}

variable "earliest_time" {
  type        = string
  description = "Earliest time for the search window"
  default     = "-1h@h" # 1 hour ago
}

variable "latest_time" {
  type        = string
  description = "Latest time for the search window"
  default     = "now"
}

variable "alert_condition" {
  type        = string
  description = "Condition that triggers the alert"
  default     = "search count > 0"
}

variable "webhook_url" {
  type        = string
  description = "Webhook URL for alert notifications (optional)"
  default     = null
}
