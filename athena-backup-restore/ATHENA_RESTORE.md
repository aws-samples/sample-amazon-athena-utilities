# Athena Restore Script

Recreate your Amazon Athena workgroups, prepared statements, named queries, and data catalogs in any AWS region from a backup JSON file. The restore process preserves configurations, tags, and workgroup state, and annotates restored resources with source traceability metadata.

## Prerequisites

```bash
pip install boto3
```

Ensure AWS credentials are configured (via `~/.aws/credentials`, environment variables, or IAM role).

## Usage

### Basic Examples

```bash
# Restore all workgroups to us-west-2
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_us_east_1.json

# Restore specific workgroups
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_us_east_1.json \
    --workgroups prod-workgroup

# Skip workgroups that already exist
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_us_east_1.json \
    --skip-existing

# Update existing workgroups with backup configuration
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_us_east_1.json \
    --update-existing

# Dry run (preview without making changes)
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_us_east_1.json \
    --dry-run

# Use specific AWS profile
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_us_east_1.json \
    --profile production
```

## Command-Line Options

| Option | Required | Description |
|--------|----------|-------------|
| `--region` | Yes | Target AWS region (e.g., us-west-2) |
| `--input` | Yes | Input backup JSON file path |
| `--workgroups` | No | Specific workgroups to restore (default: all) |
| `--skip-existing` | No | Skip workgroups that already exist |
| `--update-existing` | No | Update existing workgroups |
| `--dry-run` | No | Preview without making changes |
| `--profile` | No | AWS profile name |

**Note:** `--skip-existing` and `--update-existing` are mutually exclusive.

## Description Annotation

During restore, descriptions are automatically annotated with source information for traceability:

**Workgroups:**
```
[Backup: source_region=us-east-1, source_account=123456789012, source_workgroup=prod-workgroup]
```

**Prepared Statements:**
```
[Backup: source_region=us-east-1, source_account=123456789012, source_workgroup=prod-workgroup]
```

**Named Queries:**
```
[Backup: source_region=us-east-1, source_account=123456789012, source_workgroup=prod-workgroup]
```

**Data Catalogs:**
```
[Backup: source_region=us-east-1, source_account=123456789012, source_catalog=my-catalog]
```

These annotations are appended to the original descriptions, providing clear traceability of the backup source.

## IAM Permissions Required

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "athena:GetWorkGroup",
        "athena:CreateWorkGroup",
        "athena:UpdateWorkGroup",
        "athena:TagResource",
        "athena:CreatePreparedStatement",
        "athena:UpdatePreparedStatement",
        "athena:GetPreparedStatement",
        "athena:CreateNamedQuery",
        "athena:ListNamedQueries",
        "athena:GetNamedQuery",
        "athena:CreateDataCatalog",
        "athena:UpdateDataCatalog",
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
Backup Information:
  Source Region: us-east-1
  Source Account ID: 123456789012
  Timestamp: 2026-03-03T12:00:00
  Workgroup Count: 5

Target Region: us-west-2
Workgroups to restore: 5

Restoring 2 data catalog(s)...
  Restored 2 data catalog(s)

Restoring workgroups...
  - prod-workgroup
    Created successfully
      Restored 3 prepared statement(s)
      Restored 2 named query(ies)
  - staging-workgroup
    Created successfully
      Restored 1 prepared statement(s)
  - dev-workgroup
    Created successfully

Restore completed!
  Workgroups: 5 successful, 0 failed/skipped
```

## Common Workflows

### Full Region Failover

```bash
# 1. Backup from primary region
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_$(date +%Y%m%d_%H%M%S).json

# 2. Restore to secondary region
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_20260303_120000.json
```

### Selective Workgroup Migration

```bash
# 1. Backup specific workgroups
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_critical.json \
    --workgroups prod-analytics prod-reporting

# 2. Restore to new region
python athena_restore.py \
    --region eu-west-1 \
    --input backups/athena_critical.json
```

### Testing Restore Process

```bash
# 1. Backup from production
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_test.json

# 2. Dry run restore to verify
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_test.json \
    --dry-run

# 3. Actual restore
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_test.json
```

### Incremental Updates

```bash
# Update existing workgroups with new configuration
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_latest.json \
    --update-existing
```

## Restore Behavior

### Data Catalogs
- Restored first (before workgroups)
- Existing catalogs are updated
- New catalogs are created
- Tags are restored

### Workgroups
- Created if they don't exist
- Skipped if they exist (with `--skip-existing`)
- Updated if they exist (with `--update-existing`)
- State (ENABLED/DISABLED) is preserved
- Tags are restored

### Prepared Statements
- Created if they don't exist
- Updated if they exist
- Descriptions are annotated with source information

### Named Queries
- Created if they don't exist
- Duplicates (same name) are skipped
- Descriptions are annotated with source information

## Troubleshooting

### "AWS credentials not found"
- Configure credentials: `aws configure`
- Or use `--profile` flag with a configured profile

### "Workgroup exists" error
- Use `--skip-existing` to skip existing workgroups
- Use `--update-existing` to update them
- Or manually delete conflicting workgroups first

### "Invalid backup file format" error
- Verify the backup file is valid JSON
- Ensure the backup file was created by the backup script
- Check that the file is not corrupted

### Permission denied errors
- Verify IAM permissions (see above)
- Check that the AWS profile/credentials have appropriate access

### Throttling errors
- The script automatically retries with exponential backoff
- If persistent, consider restoring workgroups in smaller batches

## Notes

- The restore process adds backup source annotations to descriptions for traceability
- Workgroup state (ENABLED/DISABLED) is preserved from the backup
- Tags are restored for workgroups and data catalogs
- Prepared statements can be created or updated
- Named queries with duplicate names are skipped (cannot be updated)
- Data catalogs are restored before workgroups (workgroups may reference them)
- The script handles pagination automatically for large numbers of resources
- Throttling is handled with automatic retry and exponential backoff
