# Athena Backup Script

Export your Amazon Athena workgroups, prepared statements, named queries, and data catalogs from any AWS region into a single JSON file. The backup captures full configurations including tags, encryption settings, engine versions, and workgroup state so you have everything needed for a restore.

## Prerequisites

```bash
pip install boto3
```

Ensure AWS credentials are configured (via `~/.aws/credentials`, environment variables, or IAM role).

## Usage

### Basic Examples

```bash
# Backup all workgroups from us-east-1
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_us_east_1.json

# Backup specific workgroups
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_us_east_1.json \
    --workgroups prod-workgroup staging-workgroup

# Use specific AWS profile
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_us_east_1.json \
    --profile production

# Timestamped backup for versioning
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_$(date +%Y%m%d_%H%M%S).json
```

## Command-Line Options

| Option | Required | Description |
|--------|----------|-------------|
| `--region` | Yes | Source AWS region (e.g., us-east-1) |
| `--output` | Yes | Output JSON file path |
| `--workgroups` | No | Specific workgroups to backup (default: all) |
| `--profile` | No | AWS profile name |

## Backup File Format

The backup JSON includes:

### Metadata
- Timestamp of backup
- Source region
- Source account ID
- Workgroup count

### Per Workgroup
- Name, description, configuration, and state (ENABLED or DISABLED)
- Source region, account ID, and workgroup name
- Tags associated with the workgroup
- Prepared statements
- Named queries

### Data Catalogs
- Custom data catalog configurations with tags
- AWS managed catalogs (like AwsDataCatalog) are excluded

**Note:** All workgroups are backed up regardless of their state (both ENABLED and DISABLED).

## IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "athena:ListWorkGroups",
        "athena:GetWorkGroup",
        "athena:ListTagsForResource",
        "athena:ListPreparedStatements",
        "athena:GetPreparedStatement",
        "athena:ListNamedQueries",
        "athena:GetNamedQuery",
        "athena:ListDataCatalogs",
        "athena:GetDataCatalog",
        "sts:GetCallerIdentity"
      ],
      "Resource": "*"
    }
  ]
}
```

## Output Example

```
Backing up data catalogs...
  Account ID: 123456789012
  Found 2 custom data catalog(s)

Discovering workgroups...
Found 5 workgroups

Backing up 5 workgroups...
  - prod-workgroup
  - staging-workgroup
  - dev-workgroup
  - analytics-workgroup
  - reporting-workgroup

Successfully backed up 5/5 workgroups

Backup completed successfully!
Output file: backups/athena_us_east_1.json

Backup Summary:
  Workgroups: 5
  Prepared Statements: 12
  Named Queries: 8
  Data Catalogs: 2
```

## Common Use Cases

### Regular Scheduled Backups

```bash
# Daily backup with timestamp
python athena_backup.py \
    --region us-east-1 \
    --output backups/daily/athena_$(date +%Y%m%d).json
```

### Pre-Migration Backup

```bash
# Backup before major changes
python athena_backup.py \
    --region us-east-1 \
    --output backups/pre_migration_$(date +%Y%m%d_%H%M%S).json
```

### Selective Backup

```bash
# Backup only critical workgroups
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_critical.json \
    --workgroups prod-analytics prod-reporting
```

## Troubleshooting

### "AWS credentials not found"
- Configure credentials: `aws configure`
- Or use `--profile` flag with a configured profile

### "Failed to list workgroups" error
- Verify IAM permissions include `athena:ListWorkGroups`
- Check that the region is correct and accessible

### Permission denied errors
- Verify IAM permissions (see above)
- Check that the AWS profile/credentials have appropriate access

### Throttling errors
- The script automatically retries with exponential backoff
- If persistent, consider backing up workgroups in smaller batches

## Notes

- Backup files are JSON and can be version controlled
- The script preserves all workgroup configurations including result locations, encryption settings, and engine versions
- Both ENABLED and DISABLED workgroups are backed up
- Tags are backed up for workgroups and data catalogs
- Prepared statements and named queries are backed up per workgroup
- The script handles pagination automatically for large numbers of resources
- Throttling is handled with automatic retry and exponential backoff
