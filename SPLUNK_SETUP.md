# Splunk Cloud Setup Guide

This guide will help you set up your Splunk Cloud instance to work with this Detection-as-Code pipeline.

## Prerequisites

- Splunk Cloud instance (trial or paid)
- Admin access to your Splunk Cloud instance
- GitHub account with access to this repository

## 1. Splunk Cloud Instance Setup

### Get Your Splunk Cloud URL

Your Splunk Cloud management URL will look like:
```
https://your-instance.splunkcloud.com:8089
```

**Note**: Port `8089` is the Splunk management port for API access (not the web UI port 8000).

### Enable API Access

1. Log into your Splunk Cloud instance web UI
2. Navigate to **Settings** → **Server Settings** → **General Settings**
3. Ensure "Enable Splunk Web SSL" is checked
4. Note your instance URL

## 2. Create Admin User for Terraform

It's recommended to create a dedicated admin account for automation:

1. Go to **Settings** → **Access controls** → **Users**
2. Click **New User**
3. Fill in the details:
   - **Username**: `terraform-admin` (or your preferred name)
   - **Full Name**: Terraform Automation
   - **Email**: your-email@example.com
   - **Password**: Generate a strong password
   - **Roles**: `admin` role

4. Save the credentials securely

## 3. Configure GitHub Secrets

In your GitHub repository, add the following secrets:

### Navigate to Repository Settings
1. Go to your repository on GitHub
2. Click **Settings** → **Secrets and variables** → **Actions**
3. Click **New repository secret**

### Add Splunk Secrets

Create these three secrets:

#### TF_VAR_SPLUNK_URL
- **Name**: `TF_VAR_SPLUNK_URL`
- **Value**: `https://your-instance.splunkcloud.com:8089`
- **Example**: `https://prd-p-abc123.splunkcloud.com:8089`

#### TF_VAR_SPLUNK_USERNAME
- **Name**: `TF_VAR_SPLUNK_USERNAME`
- **Value**: `terraform-admin` (or the username you created)

#### TF_VAR_SPLUNK_PASSWORD
- **Name**: `TF_VAR_SPLUNK_PASSWORD`
- **Value**: The password for your Terraform admin user

## 4. Verify Connectivity

Test the connection from your local machine before deploying:

```bash
# Test API connectivity
curl -k -u terraform-admin:your-password \
  https://your-instance.splunkcloud.com:8089/services/server/info

# You should see XML output with server information
```

## 5. Configure Data Inputs (Optional)

To ensure your detection rules can find data, set up data inputs:

### For Okta Logs:
1. Go to **Settings** → **Add Data**
2. Select **Monitor** → **HTTP Event Collector**
3. Create a new HEC token for Okta logs
4. Configure your Okta to send logs to Splunk HEC endpoint
5. Set the sourcetype to `okta:system`

### Verify Data is Flowing:
```spl
index=* sourcetype=okta:system
| head 10
```

## 6. Understanding Terraform Deployment

The Terraform configuration will:

1. **Create an App**: `detection_as_code` app to store all detection rules
2. **Deploy Saved Searches**: Each Sigma rule becomes a scheduled saved search
3. **Configure Alerts**: Saved searches trigger when conditions are met
4. **Set Schedules**: Runs every 5 minutes by default

## 7. Splunk Cloud Considerations

### API Rate Limits
- Splunk Cloud has API rate limits
- The pipeline handles this automatically with retries
- For large deployments, consider batch operations

### App Permissions
- Deployed saved searches are stored in the `detection_as_code` app
- Searches are visible to all users with app access
- Modify `acl` settings in `modules/splunk_savedsearch/main.tf` to change this

### Search Time Ranges
- Default: `-1h@h` to `now` (last hour)
- Modify in `splunk_sigma_rules.tf` for different ranges
- Consider your data retention and search load

## 8. Post-Deployment Verification

After running the GitHub Actions workflow:

1. Log into Splunk Cloud web UI
2. Go to **Apps** → **detection_as_code**
3. Click **Searches, Reports, and Alerts**
4. Verify your rules are listed
5. Check the **Schedule** column shows they're enabled
6. Run a manual search to test:
   ```spl
   index=* sourcetype=okta:system eventType="user.account.privilege.grant"
   ```

## 9. Troubleshooting

### "Connection Refused" Error
- Verify port `8089` is correct
- Check your Splunk Cloud firewall allows your GitHub Actions IP
- Ensure SSL/TLS is properly configured

### "Authentication Failed" Error
- Double-check username and password in GitHub secrets
- Verify the user has `admin` role
- Try logging in manually first

### "App Already Exists" Error
- The app was created in a previous run
- This is normal - Terraform will update it
- To start fresh, manually delete the app in Splunk first

### Saved Search Not Running
- Check the schedule: `*/5 * * * *` = every 5 minutes
- Verify the search syntax is valid SPL
- Check for errors in **Settings** → **Searches, reports, and alerts**

## 10. Webhook Integration (Optional)

To send alerts to external systems:

1. In `modules/splunk_savedsearch/variables.tf`, the `webhook_url` is available
2. Configure it in your rule files:
   ```hcl
   webhook_url = "https://your-webhook-endpoint.com/alerts"
   ```
3. Splunk will POST alert data to this URL when triggered

## 11. Best Practices

1. **Use Separate Environments**: Different Splunk instances for dev/prod
2. **Test Locally First**: Use `terraform plan` before applying
3. **Monitor API Usage**: Check Splunk Cloud API usage regularly
4. **Version Control**: All rule changes go through Git
5. **Regular Backups**: Export saved searches periodically
6. **Index Optimization**: Ensure relevant indexes are configured
7. **Performance**: Monitor search load and adjust schedules

## 12. Migration from Sumo Logic

If migrating from Sumo Logic:

1. Export existing detection rules
2. Convert to Sigma format (manual or automated)
3. Test Sigma rules locally with sigma-cli
4. Deploy gradually (start with a few rules)
5. Verify alerting works as expected
6. Migrate remaining rules
7. Decommission Sumo Logic deployment

## Additional Resources

- [Splunk Cloud Documentation](https://docs.splunk.com/Documentation/SplunkCloud)
- [Splunk REST API Reference](https://docs.splunk.com/Documentation/Splunk/latest/RESTREF/RESTprolog)
- [Sigma Rule Specification](https://github.com/SigmaHQ/sigma-specification)
- [Terraform Splunk Provider](https://registry.terraform.io/providers/splunk/splunk/latest/docs)
