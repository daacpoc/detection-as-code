# Quick Start: Splunk Cloud Setup

Follow these steps to get your Detection-as-Code pipeline working with Splunk Cloud.

## Step 1: Get Your Splunk Cloud Information

1. Log into your Splunk Cloud instance
2. Note your management URL (ends with `:8089`):
   - Format: `https://your-instance.splunkcloud.com:8089`
   - Example: `https://prd-p-abc123.splunkcloud.com:8089`

## Step 2: Create Terraform Admin User in Splunk

1. In Splunk web UI, go to: **Settings** → **Users** → **New User**
2. Create user with these settings:
   - Username: `terraform-admin`
   - Password: [Generate strong password]
   - Role: `admin`
3. Save this username and password securely

## Step 3: Add GitHub Secrets

In your GitHub repository (`daacpoc/detection-as-code`):

1. Go to: **Settings** → **Secrets and variables** → **Actions**
2. Delete old Sumo Logic secrets (if they exist):
   - `TF_VAR_SUMOLOGIC_ACCESS_ID`
   - `TF_VAR_SUMOLOGIC_ACCESS_KEY`

3. Add three new secrets:

### Secret 1: Splunk URL
- Name: `TF_VAR_SPLUNK_URL`
- Value: `https://your-instance.splunkcloud.com:8089`

### Secret 2: Splunk Username
- Name: `TF_VAR_SPLUNK_USERNAME`
- Value: `terraform-admin`

### Secret 3: Splunk Password
- Name: `TF_VAR_SPLUNK_PASSWORD`
- Value: [Your terraform-admin password]

## Step 4: Test the Connection

Run this from your local machine to verify credentials:

```bash
curl -k -u terraform-admin:YOUR_PASSWORD \
  https://your-instance.splunkcloud.com:8089/services/server/info
```

You should see XML output with server information.

## Step 5: Configure Data Inputs (For Okta Rules)

To use the Okta detection rules, you need Okta data in Splunk:

### Option A: Splunk Add-on for Okta
1. Install "Splunk Add-on for Okta" from Splunkbase
2. Configure it with your Okta API token
3. Data will flow with sourcetype `okta:system`

### Option B: HTTP Event Collector (HEC)
1. In Splunk: **Settings** → **Data inputs** → **HTTP Event Collector**
2. Create new HEC token for Okta
3. Configure Okta to send logs to HEC endpoint
4. Set sourcetype to `okta:system`

### Verify Data:
```spl
index=* sourcetype=okta:system | head 10
```

## Step 6: Run the Workflow

1. Make a commit to trigger the workflow, or
2. Go to **Actions** tab in GitHub
3. Select "Deploy to Prod" workflow
4. Click "Run workflow"

## Step 7: Verify Deployment in Splunk

After workflow completes:

1. Log into Splunk Cloud web UI
2. Go to: **Apps** → **detection_as_code**
3. Click: **Searches, Reports, and Alerts**
4. You should see your detection rules listed
5. Check they're scheduled (green checkmark in Schedule column)

## Step 8: Test a Detection Rule

Run this search manually to test the Okta admin role rule:

```spl
index=* sourcetype=okta:system eventType="user.account.privilege.grant"
| search NOT target{}.alternateId="admin.*"
```

If you see results, the rule is working!

## Troubleshooting

### Authentication Failed
- Double-check secrets in GitHub match Splunk credentials
- Verify user has `admin` role in Splunk
- Try logging in manually first

### No Data Found
- Ensure Okta logs are flowing into Splunk
- Check sourcetype is `okta:system`
- Verify index permissions

### App Not Created
- Check Terraform logs in GitHub Actions
- Verify API connectivity (Step 4)
- Check Splunk Cloud firewall settings

## Next Steps

- Add more Sigma rules to `sigma_rules/` directory
- Customize schedule in `splunk_sigma_rules.tf`
- Set up webhook alerts (optional)
- Review SPLUNK_SETUP.md for detailed configuration

## Support

For detailed setup and troubleshooting, see:
- `SPLUNK_SETUP.md` - Comprehensive setup guide
- `sigma_rules/README.md` - Sigma rule documentation
- [Splunk Cloud Docs](https://docs.splunk.com/Documentation/SplunkCloud)
