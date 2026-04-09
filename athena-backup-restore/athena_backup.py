#!/usr/bin/env python3
"""
Athena Workgroup Backup Script

This script backs up Athena workgroup configurations from a source region
to a JSON file.
"""

import argparse
import json
import sys
import time
from datetime import datetime
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


def backup_prepared_statements(athena_client: Any, workgroup_name: str) -> List[Dict[str, Any]]:
    """Backup prepared statements for a workgroup."""
    prepared_statements = []
    try:
        # Try pagination first
        try:
            paginator = athena_client.get_paginator("list_prepared_statements")
            for page in paginator.paginate(WorkGroup=workgroup_name):
                for stmt in page.get("PreparedStatements", []):
                    try:
                        # Get full prepared statement details
                        detail_response = retry_with_backoff(
                            lambda: athena_client.get_prepared_statement(
                                StatementName=stmt["StatementName"],
                                WorkGroup=workgroup_name
                            )
                        )
                        ps_detail = detail_response["PreparedStatement"]
                        prepared_statements.append({
                            "StatementName": ps_detail["StatementName"],
                            "QueryStatement": ps_detail["QueryStatement"],
                            "Description": ps_detail.get("Description", ""),
                            "LastModifiedTime": ps_detail.get("LastModifiedTime", datetime.now()).isoformat(),
                        })
                    except ClientError as e:
                        error_code = e.response["Error"]["Code"]
                        if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                            print(f"      Warning: Could not backup prepared statement {stmt['StatementName']}: {e}")
        except Exception:
            # Fallback to manual pagination
            next_token = None
            while True:
                if next_token:
                    response = athena_client.list_prepared_statements(
                        WorkGroup=workgroup_name,
                        NextToken=next_token
                    )
                else:
                    response = athena_client.list_prepared_statements(WorkGroup=workgroup_name)
                
                for stmt in response.get("PreparedStatements", []):
                    try:
                        detail_response = retry_with_backoff(
                            lambda: athena_client.get_prepared_statement(
                                StatementName=stmt["StatementName"],
                                WorkGroup=workgroup_name
                            )
                        )
                        ps_detail = detail_response["PreparedStatement"]
                        prepared_statements.append({
                            "StatementName": ps_detail["StatementName"],
                            "QueryStatement": ps_detail["QueryStatement"],
                            "Description": ps_detail.get("Description", ""),
                            "LastModifiedTime": ps_detail.get("LastModifiedTime", datetime.now()).isoformat(),
                        })
                    except ClientError as e:
                        error_code = e.response["Error"]["Code"]
                        if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                            print(f"      Warning: Could not backup prepared statement {stmt['StatementName']}: {e}")
                
                next_token = response.get("NextToken")
                if not next_token:
                    break
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidRequestException":
            print(f"      Warning: Could not list prepared statements: {e}")
    
    return prepared_statements


def backup_named_queries(athena_client: Any, workgroup_name: str) -> List[Dict[str, Any]]:
    """Backup named queries for a workgroup."""
    named_queries = []
    try:
        # Try pagination first
        try:
            paginator = athena_client.get_paginator("list_named_queries")
            for page in paginator.paginate(WorkGroup=workgroup_name):
                for query_id in page.get("NamedQueryIds", []):
                    try:
                        # Get full named query details
                        detail_response = retry_with_backoff(
                            lambda qid=query_id: athena_client.get_named_query(NamedQueryId=qid)
                        )
                        nq_detail = detail_response["NamedQuery"]
                        named_queries.append({
                            "Name": nq_detail["Name"],
                            "Description": nq_detail.get("Description", ""),
                            "Database": nq_detail["Database"],
                            "QueryString": nq_detail["QueryString"],
                            "NamedQueryId": nq_detail["NamedQueryId"],
                        })
                    except ClientError as e:
                        error_code = e.response["Error"]["Code"]
                        if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                            print(f"      Warning: Could not backup named query {query_id}: {e}")
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
                    try:
                        detail_response = retry_with_backoff(
                            lambda qid=query_id: athena_client.get_named_query(NamedQueryId=qid)
                        )
                        nq_detail = detail_response["NamedQuery"]
                        named_queries.append({
                            "Name": nq_detail["Name"],
                            "Description": nq_detail.get("Description", ""),
                            "Database": nq_detail["Database"],
                            "QueryString": nq_detail["QueryString"],
                            "NamedQueryId": nq_detail["NamedQueryId"],
                        })
                    except ClientError as e:
                        error_code = e.response["Error"]["Code"]
                        if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                            print(f"      Warning: Could not backup named query {query_id}: {e}")
                
                next_token = response.get("NextToken")
                if not next_token:
                    break
    except ClientError as e:
        if e.response["Error"]["Code"] != "InvalidRequestException":
            print(f"      Warning: Could not list named queries: {e}")
    
    return named_queries


def backup_data_catalogs(athena_client: Any, region: str, account_id: str = "*") -> List[Dict[str, Any]]:
    """Backup data catalog configurations."""
    catalogs = []
    try:
        # Try pagination first
        try:
            paginator = athena_client.get_paginator("list_data_catalogs")
            for page in paginator.paginate():
                for catalog_summary in page.get("DataCatalogsSummary", []):
                    catalog_name = catalog_summary["CatalogName"]
                    # Skip AWS managed catalogs
                    if catalog_name in ["AwsDataCatalog"]:
                        continue
                    
                    try:
                        detail_response = retry_with_backoff(
                            lambda name=catalog_name: athena_client.get_data_catalog(Name=name)
                        )
                        catalog_detail = detail_response["DataCatalog"]
                        
                        catalog_data = {
                            "Name": catalog_detail["Name"],
                            "Type": catalog_detail["Type"],
                            "Description": catalog_detail.get("Description", ""),
                            "Parameters": catalog_detail.get("Parameters", {}),
                        }
                        
                        # Get tags for the data catalog
                        try:
                            catalog_arn = f"arn:aws:athena:{region}:{account_id}:datacatalog/{catalog_name}"
                            tags_response = retry_with_backoff(
                                lambda: athena_client.list_tags_for_resource(ResourceARN=catalog_arn)
                            )
                            catalog_data["Tags"] = tags_response.get("Tags", [])
                        except ClientError as e:
                            error_code = e.response["Error"]["Code"]
                            if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                                print(f"      Warning: Could not get tags for catalog {catalog_name}: {e}")
                            catalog_data["Tags"] = []
                        
                        catalogs.append(catalog_data)
                    except ClientError as e:
                        error_code = e.response["Error"]["Code"]
                        if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                            print(f"    Warning: Could not backup data catalog {catalog_name}: {e}")
        except Exception:
            # Fallback to manual pagination
            next_token = None
            while True:
                if next_token:
                    response = athena_client.list_data_catalogs(NextToken=next_token)
                else:
                    response = athena_client.list_data_catalogs()
                
                for catalog_summary in response.get("DataCatalogsSummary", []):
                    catalog_name = catalog_summary["CatalogName"]
                    if catalog_name in ["AwsDataCatalog"]:
                        continue
                    
                    try:
                        detail_response = retry_with_backoff(
                            lambda name=catalog_name: athena_client.get_data_catalog(Name=name)
                        )
                        catalog_detail = detail_response["DataCatalog"]
                        
                        catalog_data = {
                            "Name": catalog_detail["Name"],
                            "Type": catalog_detail["Type"],
                            "Description": catalog_detail.get("Description", ""),
                            "Parameters": catalog_detail.get("Parameters", {}),
                        }
                        
                        # Get tags for the data catalog
                        try:
                            catalog_arn = f"arn:aws:athena:{region}:{account_id}:datacatalog/{catalog_name}"
                            tags_response = retry_with_backoff(
                                lambda: athena_client.list_tags_for_resource(ResourceARN=catalog_arn)
                            )
                            catalog_data["Tags"] = tags_response.get("Tags", [])
                        except ClientError as e:
                            error_code = e.response["Error"]["Code"]
                            if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                                print(f"      Warning: Could not get tags for catalog {catalog_name}: {e}")
                            catalog_data["Tags"] = []
                        
                        catalogs.append(catalog_data)
                    except ClientError as e:
                        error_code = e.response["Error"]["Code"]
                        if error_code not in ["ThrottlingException", "TooManyRequestsException"]:
                            print(f"    Warning: Could not backup data catalog {catalog_name}: {e}")
                
                next_token = response.get("NextToken")
                if not next_token:
                    break
    except ClientError as e:
        print(f"    Warning: Could not list data catalogs: {e}")
    
    return catalogs


def backup_workgroup(athena_client: Any, workgroup_name: str, region: str, account_id: str) -> Dict[str, Any]:
    """Backup a single workgroup configuration with associated resources."""
    try:
        response = retry_with_backoff(
            lambda: athena_client.get_work_group(WorkGroup=workgroup_name)
        )
        workgroup = response["WorkGroup"]
        
        # Extract relevant configuration
        backup_data = {
            "Name": workgroup["Name"],
            "Description": workgroup.get("Description", ""),
            "Configuration": workgroup.get("Configuration", {}),
            "State": workgroup.get("State", "ENABLED"),
            "CreationTime": workgroup.get("CreationTime", datetime.now()).isoformat(),
            "SourceRegion": region,
            "SourceAccountId": account_id,
            "SourceWorkgroupName": workgroup["Name"],
        }
        
        # Get tags if available
        try:
            tags_response = retry_with_backoff(
                lambda: athena_client.list_tags_for_resource(
                    ResourceARN=f"arn:aws:athena:{athena_client.meta.region_name}:*:workgroup/{workgroup_name}"
                )
            )
            backup_data["Tags"] = tags_response.get("Tags", [])
        except ClientError:
            backup_data["Tags"] = []
        
        # Backup prepared statements
        backup_data["PreparedStatements"] = backup_prepared_statements(athena_client, workgroup_name)
        
        # Backup named queries
        backup_data["NamedQueries"] = backup_named_queries(athena_client, workgroup_name)
        
        return backup_data
    
    except ClientError as e:
        print(f"Error backing up workgroup {workgroup_name}: {e}")
        raise


def list_workgroups(athena_client: Any) -> List[str]:
    """List all workgroups in the region (both ENABLED and DISABLED)."""
    workgroups = []
    
    try:
        # Try pagination first
        try:
            paginator = athena_client.get_paginator("list_work_groups")
            for page in paginator.paginate():
                for wg in page.get("WorkGroups", []):
                    workgroups.append(wg["Name"])
        except Exception:
            # Fallback to manual pagination if paginator not available
            next_token = None
            while True:
                if next_token:
                    response = athena_client.list_work_groups(NextToken=next_token)
                else:
                    response = athena_client.list_work_groups()
                
                for wg in response.get("WorkGroups", []):
                    workgroups.append(wg["Name"])
                
                next_token = response.get("NextToken")
                if not next_token:
                    break
    except ClientError as e:
        print(f"Error listing workgroups: {e}")
        raise
    
    return workgroups


def main():
    parser = argparse.ArgumentParser(
        description="Backup Athena workgroup configurations"
    )
    parser.add_argument(
        "--region",
        required=True,
        help="AWS region to backup from (e.g., us-east-1)"
    )
    parser.add_argument(
        "--output",
        required=True,
        help="Output JSON file path for backup data"
    )
    parser.add_argument(
        "--workgroups",
        nargs="+",
        help="Specific workgroups to backup (default: all workgroups)"
    )
    parser.add_argument(
        "--profile",
        help="AWS profile to use (optional)"
    )
    
    args = parser.parse_args()
    
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
    
    # Get workgroups to backup
    try:
        if args.workgroups:
            workgroups_to_backup = args.workgroups
        else:
            print("Discovering workgroups...")
            workgroups_to_backup = list_workgroups(athena_client)
            print(f"Found {len(workgroups_to_backup)} workgroups")
    except Exception as e:
        print(f"Failed to list workgroups: {e}")
        sys.exit(1)
    
    # Backup data catalogs (once for all workgroups)
    print("\nBacking up data catalogs...")
    # Try to get account ID from STS, fallback to wildcard
    try:
        sts_client = session.client("sts")
        account_id = sts_client.get_caller_identity()["Account"]
        print(f"  Account ID: {account_id}")
    except Exception:
        account_id = "*"
        print(f"  Warning: Could not determine account ID")
    
    data_catalogs = backup_data_catalogs(athena_client, args.region, account_id)
    if data_catalogs:
        print(f"  Found {len(data_catalogs)} custom data catalog(s)")
    
    # Backup workgroups
    backup_data = {
        "backup_metadata": {
            "timestamp": datetime.now().isoformat(),
            "source_region": args.region,
            "source_account_id": account_id,
            "workgroup_count": len(workgroups_to_backup),
            "data_catalog_count": len(data_catalogs)
        },
        "data_catalogs": data_catalogs,
        "workgroups": []
    }
    
    print(f"\nBacking up {len(workgroups_to_backup)} workgroups...")
    successful_backups = 0
    for workgroup_name in workgroups_to_backup:
        try:
            print(f"  - {workgroup_name}")
            wg_backup = backup_workgroup(athena_client, workgroup_name, args.region, account_id)
            backup_data["workgroups"].append(wg_backup)
            successful_backups += 1
        except Exception as e:
            print(f"    Failed: {e}")
            continue
    
    print(f"\nSuccessfully backed up {successful_backups}/{len(workgroups_to_backup)} workgroups")
    
    # Calculate summary statistics
    total_prepared_statements = sum(
        len(wg.get("PreparedStatements", [])) for wg in backup_data["workgroups"]
    )
    total_named_queries = sum(
        len(wg.get("NamedQueries", [])) for wg in backup_data["workgroups"]
    )
    total_catalogs = len(backup_data.get("data_catalogs", []))
    
    # Add resource counts to metadata
    backup_data["backup_metadata"]["prepared_statement_count"] = total_prepared_statements
    backup_data["backup_metadata"]["named_query_count"] = total_named_queries
    
    # Write backup to file
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    try:
        with open(output_path, "w") as f:
            json.dump(backup_data, f, indent=2, default=str)
        
        print(f"\nBackup completed successfully!")
        print(f"Output file: {output_path}")
        print(f"\nBackup Summary:")
        print(f"  Workgroups: {len(backup_data['workgroups'])}")
        print(f"  Prepared Statements: {total_prepared_statements}")
        print(f"  Named Queries: {total_named_queries}")
        print(f"  Data Catalogs: {total_catalogs}")
    except Exception as e:
        print(f"Error writing backup file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
