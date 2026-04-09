# Amazon Athena Backup and Restore

Back up and restore your Amazon Athena workgroups, prepared statements, named queries, and data catalogs across AWS regions. Use these scripts for disaster recovery, cross-region migration, or to maintain point-in-time snapshots of your Athena configurations.

## Overview

These scripts provide a solution for:
- Disaster recovery and business continuity
- Cross-region migration of Athena resources
- Environment replication (prod → staging/dev)
- JSON output format compatible with version control systems

## Quick Start

### Installation

```bash
pip install boto3
```

Configure AWS credentials:
```bash
aws configure
```

### Backup

```bash
python athena_backup.py \
    --region us-east-1 \
    --output backups/athena_backup.json
```

### Restore

```bash
python athena_restore.py \
    --region us-west-2 \
    --input backups/athena_backup.json
```

## Documentation

- **[Backup Guide](ATHENA_BACKUP.md)** - Complete backup script documentation
- **[Restore Guide](ATHENA_RESTORE.md)** - Complete restore script documentation

## What Gets Backed Up

- **Workgroups** (ENABLED and DISABLED)
  - Configuration (result location, encryption, engine version)
  - Tags
  - State
- **Prepared Statements** (per workgroup)
- **Named Queries** (per workgroup)
- **Data Catalogs** (custom catalogs only)
  - Configuration
  - Tags

## Key Features

- **Complete Resource Coverage**: Backs up workgroups, prepared statements, named queries, and data catalogs
- **Source Traceability**: Automatically annotates restored resources with source region, account ID, and resource name
- **Flexible Restore Options**: Skip existing, update existing, or dry-run modes
- **Throttling Handling**: Automatic retry with exponential backoff
- **Selective Operations**: Backup/restore specific workgroups or all resources
- **Version Control Friendly**: JSON backup format for easy versioning

## Common Use Cases

### Disaster Recovery
```bash
# Regular backups
python athena_backup.py --region us-east-1 --output backups/daily_$(date +%Y%m%d).json

# Restore to DR region
python athena_restore.py --region us-west-2 --input backups/daily_20260303.json
```

### Cross-Region Migration
```bash
# Backup from source region
python athena_backup.py --region us-east-1 --output migration.json

python athena_restore.py --region eu-west-1 --input migration.json
```

## IAM Permissions

### Backup Permissions
- `athena:ListWorkGroups`, `athena:GetWorkGroup`
- `athena:ListPreparedStatements`, `athena:GetPreparedStatement`
- `athena:ListNamedQueries`, `athena:GetNamedQuery`
- `athena:ListDataCatalogs`, `athena:GetDataCatalog`
- `athena:ListTagsForResource`
- `sts:GetCallerIdentity`

### Restore Permissions
- `athena:CreateWorkGroup`, `athena:UpdateWorkGroup`, `athena:GetWorkGroup`
- `athena:CreatePreparedStatement`, `athena:UpdatePreparedStatement`, `athena:GetPreparedStatement`
- `athena:CreateNamedQuery`, `athena:ListNamedQueries`, `athena:GetNamedQuery`
- `athena:CreateDataCatalog`, `athena:UpdateDataCatalog`, `athena:GetDataCatalog`
- `athena:TagResource`
- `sts:GetCallerIdentity`

See individual documentation files for complete IAM policy examples.

## Scripts

- `athena_backup.py` - Backup Athena resources to JSON
- `athena_restore.py` - Restore Athena resources from JSON

## Support

For detailed usage, examples, and troubleshooting:
- See [ATHENA_BACKUP.md](ATHENA_BACKUP.md) for backup documentation
- See [ATHENA_RESTORE.md](ATHENA_RESTORE.md) for restore documentation
