# Sumo Logic Monitor Module
# Provider configuration is inherited from root main.tf

resource "sumologic_monitor" "tf_logs_monitor_1" {
  name             = "Terraform Logs Monitor"
  description      = "tf logs monitor"
  type             = "MonitorsLibraryMonitor"
  is_disabled      = false
  content_type     = "Monitor"
  monitor_type     = "Logs"
  evaluation_delay = "5m"
  tags = {
    "team"        = "monitoring"
    "application" = "sumologic"
  }

  queries {
    row_id = "A"
    query  = "_sourceCategory=event-action info"
  }

  trigger_conditions {
    logs_static_condition {
      critical {
        time_range = "15m"
        alert {
          threshold      = 40.0
          threshold_type = "GreaterThan"
        }
        resolution {
          threshold      = 40.0
          threshold_type = "LessThanOrEqual"
        }
      }
    }
  }

  notifications {
    notification {
      connection_type = "Email"
      recipients = [
        "whatever@whatever.com",
      ]
      subject      = "Monitor Alert: {{TriggerType}} on {{Name}}"
      time_zone    = "CST"
      message_body = "Triggered {{TriggerType}} Alert on {{Name}}: {{QueryURL}}"
    }
    run_for_trigger_types = ["Critical", "ResolvedCritical"]
  }
}