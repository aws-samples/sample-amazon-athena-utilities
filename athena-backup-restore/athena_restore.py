#!/usr/bin/env python3
"""
Athena Workgroup Restore Script

This script restores Athena workgroup configurations from a backup JSON file
to a target region.
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("Error: boto3 is required. Install with: pip install boto3")
    sys.exit(1)


def retry_with_backoff(func, max_retries=5, initial_delay=1.0):
    """
    Retry a function with exponential backoff for throttling errors.
    
    Args:
        func: Function to retry (should be a lambda or callable)
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds
    
    Returns:
        Result of the function call
    """
    delay = initial_delay
    last_exception = None
    
    for attempt in range(max_retries):
        try:
            return func()
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code in ["ThrottlingException", "TooManyRequestsException", "RequestLimitExceeded"]:
                last_exception = e
                if attempt < max_retries - 1:
                    jitter = delay * 0.1  # Add 10% jitter
                    sleep_time = delay + (jitter * (0.5 - time.time() % 1))
                    print(f"        Throttled, retrying in {sleep_time:.2f}s (attempt {attempt + 1}/{max_retries})...")
                    time.sleep(sleep_time)
                    delay *= 2  # Exponential backoff
                else:
                    print(f"        Max retries reached, giving up")
                    raise
            else:
                # Non-throttling error, raise immediately
                raise
    
    # Should not reach here, but just in case
    if last_exception:
        raise last_exception


def workgroup_exists(athena_client: Any, workgroup_name: str) -> bool:
    """Check if a workgroup already exists."""
    try:
        retry_with_backoff(
            lambda: athena_client.get_work_group(WorkGroup=workgroup_name)
        )
        return True
    except ClientError as e:
        if e.response["Error"]["Code"] == "InvalidRequestException":
            return False
        raise


def restore_prepared_statements(
    athena_client: Any,
    workgroup_name: str,
    prepared_statements: List[Dict[str, Any]],
    source_region: str,
    source_account_id: str,
    source_workgroup: str
) -> int:
    """Restore prepared statements for a workgroup."""
    success_count = 0
    for ps in prepared_statements:
        try:
            # Annotate description with source information
            original_description = ps.get("Description", "")
            annotated_description = f"[Backup: source_region={source_region}, source_account={source_account_id}, source_workgroup={source_workgroup}]"
            if original_description:
                annotated_description = f"{original_description} {annotated_description}"
            
            # Check if prepared statement already exists
            try:
                retry_with_backoff(
                    lambda: athena_client.get_prepared_statement(
                        StatementName=ps["StatementName"],
                        WorkGroup=workgroup_name
                    )
                )
                # Update existing
                retry_with_backoff(
                    lambda: athena_client.update_prepared_statement(
                        StatementName=ps["StatementName"],
                        WorkGroup=workgroup_name,
                        QueryStatement=ps["QueryStatement"],
                        Description=annotated_description
                    )
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "ResourceNotFoundException":
                    # Create new
                    retry_with_backoff(
                        lambda: athena_client.create_prepared_statement(
                            StatementName=ps["StatementName"],
                            WorkGroup=workgroup_name,
                            QueryStatement=ps["QueryStatement"],
                            Description=annotated_description
                        )
                    )
                else:
                    raise
            success_count += 1
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                print(f"        Warning: Could not restore prepared statement {ps['StatementName']}: {e}")
    
    return success_count


def restore_named_queries(
    athena_client: Any,
    workgroup_name: str,
    named_queries: List[Dict[str, Any]],
    source_region: str,
    source_account_id: str,
    source_workgroup: str
) -> int:
    """Restore named queries for a workgroup."""
    success_count = 0
    for nq in named_queries:
        try:
            # Annotate description with source information
            original_description = nq.get("Description", "")
            annotated_description = f"[Backup: source_region={source_region}, source_account={source_account_id}, source_workgroup={source_workgroup}]"
            if original_description:
                annotated_description = f"{original_description} {annotated_description}"
            
            # Named queries cannot be updated, only created
            # Check if one with the same name exists
            existing_queries = []
            try:
                # Try pagination first
                try:
                    paginator = athena_client.get_paginator("list_named_queries")
                    for page in paginator.paginate(WorkGroup=workgroup_name):
                        for query_id in page.get("NamedQueryIds", []):
                            detail = retry_with_backoff(
                                lambda qid=query_id: athena_client.get_named_query(NamedQueryId=qid)
                            )
                            if detail["NamedQuery"]["Name"] == nq["Name"]:
                                existing_queries.append(query_id)
                except Exception:
                    # Fallback to manual pagination
                    next_token = None
                    while True:
                        if next_token:
                            response = athena_client.list_named_queries(
                                WorkGroup=workgroup_name,
                                NextToken=next_token
                            )
                        else:
                            response = athena_client.list_named_queries(WorkGroup=workgroup_name)
                        
                        for query_id in response.get("NamedQueryIds", []):
                            detail = retry_with_backoff(
                                lambda qid=query_id: athena_client.get_named_query(NamedQueryId=qid)
                            )
                            if detail["NamedQuery"]["Name"] == nq["Name"]:
                                existing_queries.append(query_id)
                        
                        next_token = response.get("NextToken")
                        if not next_token:
                            break
            except ClientError:
                pass
            
            if existing_queries:
                print(f"        Warning: Named query '{nq['Name']}' already exists, skipping")
                continue
            
            # Create named query
            retry_with_backoff(
                lambda: athena_client.create_named_query(
                    Name=nq["Name"],
                    Description=annotated_description,
                    Database=nq["Database"],
                    QueryString=nq["QueryString"],
                    WorkGroup=workgroup_name
                )
            )
            success_count += 1
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                print(f"        Warning: Could not restore named query {nq['Name']}: {e}")
    
    return success_count


def restore_data_catalogs(athena_client: Any, catalogs: List[Dict[str, Any]], source_region: str, source_account_id: str, target_region: str, account_id: str = "*") -> int:
    """Restore data catalog configurations."""
    success_count = 0
    for catalog in catalogs:
        try:
            # Annotate description with source information
            original_description = catalog.get("Description", "")
            annotated_description = f"[Backup: source_region={source_region}, source_account={source_account_id}, source_catalog={catalog['Name']}]"
            if original_description:
                annotated_description = f"{original_description} {annotated_description}"
            
            # Check if catalog exists
            catalog_exists = False
            try:
                retry_with_backoff(
                    lambda: athena_client.get_data_catalog(Name=catalog["Name"])
                )
                catalog_exists = True
            except ClientError as e:
                if e.response["Error"]["Code"] != "InvalidRequestException":
                    raise
            
            if catalog_exists:
                # Update existing
                retry_with_backoff(
                    lambda: athena_client.update_data_catalog(
                        Name=catalog["Name"],
                        Type=catalog["Type"],
                        Description=annotated_description,
                        Parameters=catalog.get("Parameters", {})
                    )
                )
            else:
                # Create new
                retry_with_backoff(
                    lambda: athena_client.create_data_catalog(
                        Name=catalog["Name"],
                        Type=catalog["Type"],
                        Description=annotated_description,
                        Parameters=catalog.get("Parameters", {})
                    )
                )
            
            # Restore tags if available
            if "Tags" in catalog and catalog["Tags"]:
                try:
                    catalog_arn = f"arn:aws:athena:{target_region}:{account_id}:datacatalog/{catalog['Name']}"
                    retry_with_backoff(
                        lambda: athena_client.tag_resource(
                            ResourceARN=catalog_arn,
                            Tags=catalog["Tags"]
                        )
                    )
                except ClientError as e:
                    error_code = e.response["Error"]["Code"]
                    if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                        print(f"      Warning: Could not restore tags for catalog {catalog['Name']}: {e}")
            
            success_count += 1
        except ClientError as e:
            error_code = e.response["Error"]["Code"]
            if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                print(f"    Warning: Could not restore data catalog {catalog['Name']}: {e}")
    
    return success_count


def restore_workgroup(
    athena_client: Any,
    workgroup_data: Dict[str, Any],
    skip_existing: bool = False,
    update_existing: bool = False
) -> bool:
    """Restore a single workgroup configuration."""
    workgroup_name = workgroup_data["Name"]
    
    # Annotate description with source information
    original_description = workgroup_data.get("Description", "")
    source_region = workgroup_data.get("SourceRegion", "unknown")
    source_account_id = workgroup_data.get("SourceAccountId", "unknown")
    source_workgroup = workgroup_data.get("SourceWorkgroupName", workgroup_name)
    
    annotated_description = f"[Backup: source_region={source_region}, source_account={source_account_id}, source_workgroup={source_workgroup}]"
    if original_description:
        annotated_description = f"{original_description} {annotated_description}"
    
    try:
        exists = workgroup_exists(athena_client, workgroup_name)
        
        if exists:
            if skip_existing:
                print(f"    Skipped (already exists)")
                return False
            elif update_existing:
                print(f"    Updating existing workgroup...")
                # Update workgroup configuration
                update_params = {
                    "WorkGroup": workgroup_name,
                    "Description": annotated_description,
                }
                
                if "Configuration" in workgroup_data:
                    update_params["ConfigurationUpdates"] = workgroup_data["Configuration"]
                
                if "State" in workgroup_data:
                    update_params["State"] = workgroup_data["State"]
                
                athena_client.update_work_group(**update_params)
                print(f"    Updated successfully")
                return True
            else:
                print(f"    Error: Workgroup exists (use --skip-existing or --update-existing)")
                return False
        
        # Create new workgroup
        create_params = {
            "Name": workgroup_name,
            "Description": annotated_description,
        }
        
        if "Configuration" in workgroup_data:
            create_params["Configuration"] = workgroup_data["Configuration"]
        
        if "Tags" in workgroup_data and workgroup_data["Tags"]:
            create_params["Tags"] = workgroup_data["Tags"]
        
        athena_client.create_work_group(**create_params)
        print(f"    Created successfully")
        
        # Restore prepared statements
        if "PreparedStatements" in workgroup_data and workgroup_data["PreparedStatements"]:
            ps_count = restore_prepared_statements(
                athena_client,
                workgroup_name,
                workgroup_data["PreparedStatements"],
                source_region,
                source_account_id,
                source_workgroup
            )
            if ps_count > 0:
                print(f"      Restored {ps_count} prepared statement(s)")
        
        # Restore named queries
        if "NamedQueries" in workgroup_data and workgroup_data["NamedQueries"]:
            nq_count = restore_named_queries(
                athena_client,
                workgroup_name,
                workgroup_data["NamedQueries"],
                source_region,
                source_account_id,
                source_workgroup
            )
            if nq_count > 0:
                print(f"      Restored {nq_count} named query(ies)")
        
        return True
    
    except ClientError as e:
        print(f"    Error: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Restore Athena workgroup configurations from backup"
    )
    parser.add_argument(
        "--region",
        required=True,
        help="AWS region to restore to (e.g., us-west-2)"
    )
    parser.add_argument(
        "--input",
        required=True,
        help="Input JSON file path with backup data"
    )
    parser.add_argument(
        "--workgroups",
        nargs="+",
        help="Specific workgroups to restore (default: all from backup)"
    )
    parser.add_argument(
        "--skip-existing",
        action="store_true",
        help="Skip workgroups that already exist in target region"
    )
    parser.add_argument(
        "--update-existing",
        action="store_true",
        help="Update workgroups that already exist in target region"
    )
    parser.add_argument(
        "--profile",
        help="AWS profile to use (optional)"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be restored without making changes"
    )
    
    args = parser.parse_args()
    
    # Validate mutually exclusive options
    if args.skip_existing and args.update_existing:
        print("Error: --skip-existing and --update-existing are mutually exclusive")
        sys.exit(1)
    
    # Load backup data
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Backup file not found: {input_path}")
        sys.exit(1)
    
    try:
        with open(input_path, "r") as f:
            backup_data = json.load(f)
    except Exception as e:
        print(f"Error reading backup file: {e}")
        sys.exit(1)
    
    # Validate backup data structure
    if "workgroups" not in backup_data:
        print("Error: Invalid backup file format (missing 'workgroups' key)")
        sys.exit(1)
    
    # Display backup metadata
    if "backup_metadata" in backup_data:
        metadata = backup_data["backup_metadata"]
        print(f"Backup Information:")
        print(f"  Source Region: {metadata.get('source_region', 'unknown')}")
        print(f"  Source Account ID: {metadata.get('source_account_id', 'unknown')}")
        print(f"  Timestamp: {metadata.get('timestamp', 'unknown')}")
        print(f"  Workgroup Count: {metadata.get('workgroup_count', len(backup_data['workgroups']))}")
        print(f"  Data Catalog Count: {metadata.get('data_catalog_count', len(backup_data.get('data_catalogs', [])))}")
        print(f"  Prepared Statement Count: {metadata.get('prepared_statement_count', 'unknown')}")
        print(f"  Named Query Count: {metadata.get('named_query_count', 'unknown')}")
        print()
    
    # Filter workgroups if specified
    workgroups_to_restore = backup_data["workgroups"]
    if args.workgroups:
        workgroups_to_restore = [
            wg for wg in workgroups_to_restore
            if wg["Name"] in args.workgroups
        ]
        if not workgroups_to_restore:
            print("Error: None of the specified workgroups found in backup")
            sys.exit(1)
    
    print(f"Target Region: {args.region}")
    print(f"Workgroups to restore: {len(workgroups_to_restore)}")
    
    if args.dry_run:
        print("\nDRY RUN MODE - No changes will be made\n")
        for wg in workgroups_to_restore:
            print(f"  - {wg['Name']}")
        sys.exit(0)
    
    # Initialize AWS client
    try:
        session_kwargs = {"region_name": args.region}
        if args.profile:
            session_kwargs["profile_name"] = args.profile
        
        session = boto3.Session(**session_kwargs)
        athena_client = session.client("athena")
    except NoCredentialsError:
        print("Error: AWS credentials not found")
        sys.exit(1)
    except Exception as e:
        print(f"Error initializing AWS client: {e}")
        sys.exit(1)
    
    # Restore data catalogs first
    source_region = backup_data.get("backup_metadata", {}).get("source_region", "unknown")
    source_account_id = backup_data.get("backup_metadata", {}).get("source_account_id", "unknown")
    if "data_catalogs" in backup_data and backup_data["data_catalogs"]:
        print(f"\nRestoring {len(backup_data['data_catalogs'])} data catalog(s)...")
        
        # Try to get account ID from STS, fallback to wildcard
        try:
            sts_client = session.client("sts")
            account_id = sts_client.get_caller_identity()["Account"]
        except Exception:
            account_id = "*"
        
        catalog_count = restore_data_catalogs(
            athena_client,
            backup_data["data_catalogs"],
            source_region,
            source_account_id,
            args.region,
            account_id
        )
        print(f"  Restored {catalog_count} data catalog(s)")
    
    # Restore workgroups
    print(f"\nRestoring workgroups...")
    success_count = 0
    failed_count = 0
    
    for workgroup_data in workgroups_to_restore:
        workgroup_name = workgroup_data["Name"]
        print(f"  - {workgroup_name}")
        
        try:
            if restore_workgroup(
                athena_client,
                workgroup_data,
                skip_existing=args.skip_existing,
                update_existing=args.update_existing
            ):
                success_count += 1
            else:
                failed_count += 1
        except Exception as e:
            print(f"    Unexpected error: {e}")
            failed_count += 1
    
    # Summary
    print(f"\nRestore completed!")
    print(f"  Workgroups: {success_count} successful, {failed_count} failed/skipped")


if __name__ == "__main__":
    main()
