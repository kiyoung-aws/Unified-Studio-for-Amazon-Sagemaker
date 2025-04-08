import argparse
import json
import boto3
from pprint import pprint

from botocore.exceptions import ClientError

def _parse_args():
    parser = argparse.ArgumentParser(description='Python script to bring your tables in S3 Table Bucket into a specified project in sagemaker unified studio')

    parser.add_argument('--project-role-arn', type=str, required=True, help='Project role arn of the SageMaker Unified Studio project in which you want to bring your own glue tables')
    parser.add_argument('--iam-role-arn-lf-resource-register', type=str, required=True, help='IAM Role arn which would be used in registration of S3 location in LakeFormation. Please refer to https://docs.aws.amazon.com/lake-formation/latest/dg/s3tables-catalog-prerequisites.html step3 and step4'
                        ' for role requirements.')
    parser.add_argument('--table-bucket-arn', type=str, required=True, help='Arn of S3 table bucket you want to bring into your project')
    parser.add_argument('--table-bucket-namespace', type=str, required=False, help='Namespace of S3 table bucket you want to bring into your project. If not provided, imports all the tables of the provided s3 table bucket into the project')
    parser.add_argument('--table-name', type=str, required=False, help='Name of the table created in S3 table bucket you want to bring into your project. If not provided, imports all the tables of the provided s3 table bucket namespace into the project')
    parser.add_argument('--region', type=str, required=False, help='The AWS region. If not specified, the default region from your AWS credentials will be used')
    parser.add_argument('--execute', default=False, help='Determine if the script should generate overview or do the actual work', action='store_true')

    return parser.parse_args()

def _add_lf_admin(lf_client, account_id, execute_flag):
    data_lake_settings = lf_client.get_data_lake_settings()
    print(f"Checking current Data lake administrators:")
    pprint(f"{json.dumps(data_lake_settings, sort_keys=True)}\n")
    redshift_principal = f"arn:aws:iam::{account_id}:role/aws-service-role/redshift.amazonaws.com/AWSServiceRoleForRedshift"
    if execute_flag:
        # Check if principal already exists
        principal_exists = any(
            admin.get('DataLakePrincipalIdentifier') == redshift_principal 
            for admin in data_lake_settings['DataLakeSettings']['ReadOnlyAdmins']
        )
        if not principal_exists:
            data_lake_settings['DataLakeSettings']['ReadOnlyAdmins'].append({
                'DataLakePrincipalIdentifier': f"arn:aws:iam::{account_id}:role/aws-service-role/redshift.amazonaws.com/AWSServiceRoleForRedshift"
            })
        lf_client.put_data_lake_settings(
            DataLakeSettings = data_lake_settings['DataLakeSettings']
        )
        print(f"Successfully added AWSServiceRoleForRedshift role as Data lake ReadOnlyAdmins\n")
    else:
        print(f"Skip adding AWSServiceRoleForRedshift role as Data lake ReadOnlyAdmins, set --execute flag to True to do the actual update\n")

def _register_resource(lf_client, table_bucket_arn, iam_role_arn_lf_resource_register, execute_flag):
    s3_table_bucket_account_id = table_bucket_arn.split(':')[4]
    s3_table_bucket_region = table_bucket_arn.split(':')[3]
    if execute_flag:
        try:
            lf_client.register_resource(
                ResourceArn=f"arn:aws:s3tables:{s3_table_bucket_region}:{s3_table_bucket_account_id}:bucket/*",
                WithPrivilegedAccess=True,
                RoleArn=iam_role_arn_lf_resource_register
            )
            print(f"Successfully registered {table_bucket_arn} as LakeFormation resource\n")
        except ClientError as e:
            if e.response['Error']['Code'] == 'AlreadyExistsException':
                print(f"Resource {table_bucket_arn} already registered as LakeFormation resource with {iam_role_arn_lf_resource_register} as principal\n")
            else:
                raise e
    else:
        print(f"Skip registering {table_bucket_arn} as LakeFormation resource with {iam_role_arn_lf_resource_register} as principal, set --execute flag to True to do the actual update\n")

def _create_glue_catalog(glue_client, table_bucket_arn, execute_flag):
    s3_table_bucket_account_id = table_bucket_arn.split(':')[4]
    s3_table_bucket_region = table_bucket_arn.split(':')[3]
    # Create catalog configuration
    catalog_input = {
        "Name": "s3tablescatalog",
        "CatalogInput": {
            "FederatedCatalog": {
                "Identifier": f"arn:aws:s3tables:{s3_table_bucket_region}:{s3_table_bucket_account_id}:bucket/*",
                "ConnectionName": "aws:s3tables"
            },
            "CreateDatabaseDefaultPermissions": [],
            "CreateTableDefaultPermissions": []
        }
    }
    if execute_flag:
        # Create catalog
        try:
            glue_client.create_catalog(
                **catalog_input
            )
            print(f"Successfully created glue catalog 's3tablescatalog'\n")
        except ClientError as e:
            if e.response['Error']['Code'] == 'AlreadyExistsException':
                print(f"Successfully created glue catalog 's3tablescatalog'\n")
            else:
                raise e
    else:
        print(f"Skip creating glue catalog 's3tablescatalog', set --execute flag to True to do the actual update\n")

def _grant_table_lf_permissions(lf_client, s3tables_client, table_bucket_arn, namespace, table_name, project_role_arn, execute_flag):
    account_id = table_bucket_arn.split(':')[4]
    s3_table_bucket_name = table_bucket_arn.split('/')[-1]
    # Validate whether the input `Table Name` is present within S3 Table Bucket or not
    s3tables_client.get_table(
        tableBucketARN=table_bucket_arn,
        namespace=namespace,
        name=table_name
    )
    # Create permissions configuration
    permissions_input_table = {
        "Principal": {
            "DataLakePrincipalIdentifier": project_role_arn
        },
        "Resource": {
            "Table": {
                "CatalogId": f"{account_id}:s3tablescatalog/{s3_table_bucket_name}",
                "DatabaseName": namespace,
-               "Name": table_name,
                # "TableWildcard": {}
            }
        },
        "Permissions": ["ALL"]
    }

    if execute_flag:
        lf_client.grant_permissions(
            **permissions_input_table
        )
        print(f"Successfully granted lakeformation permissions to s3 table bucket '{table_bucket_arn}', namespace '{namespace}', table '{table_name}'\n")
    else:
        print(f"Skip granting lakeformation permissions to s3 table bucket '{table_bucket_arn}', namespace '{namespace}', table '{table_name}', set --execute flag to True to do the actual update\n")
    

def _grant_s3_table_bucket_lf_permissions(lf_client, s3tables_client, project_role_arn, table_bucket_arn, 
                                          table_bucket_namespace, table_name, execute_flag):
    if not table_bucket_namespace and table_name:
        raise Exception(f"Error: Please provide namespace name along with the table name '{table_name}', or remove table name from input.")
    # Import all tables under provide S3 Table Bucket into SMUS Project
    elif not table_bucket_namespace and not table_name:
        next_token = None
        while True:
            if next_token:
                response = s3tables_client.list_tables(
                    tableBucketARN=table_bucket_arn,
                    nextToken=next_token
                )
            else:
                response = s3tables_client.list_tables(
                    tableBucketARN=table_bucket_arn
                )
            tables_list = response["tables"]
            for table in tables_list:
                for namespace in table["namespace"]:
                    _grant_table_lf_permissions(lf_client,
                                                s3tables_client,
                                                table_bucket_arn,
                                                namespace,
                                                table["name"],
                                                project_role_arn,
                                                execute_flag)
                
            if 'continuationToken' in response:
                next_token = response['continuationToken']
            else:
                break
    # Import all tables under provide S3 Table Bucket and namespace into SMUS Project
    elif table_bucket_namespace and not table_name:
        next_token = None
        while True:
            if next_token:
                response = s3tables_client.list_tables(
                    tableBucketARN=table_bucket_arn,
                    namespace=table_bucket_namespace,
                    nextToken=next_token
                )
            else:
                response = s3tables_client.list_tables(
                    tableBucketARN=table_bucket_arn,
                    namespace=table_bucket_namespace
                )
            tables_list = response["tables"]
            for table in tables_list:
                _grant_table_lf_permissions(lf_client,
                                            s3tables_client,
                                            table_bucket_arn,
                                            table_bucket_namespace,
                                            table["name"],
                                            project_role_arn,
                                            execute_flag)
                
            if 'continuationToken' in response:
                next_token = response['continuationToken']
            else:
                break
    # Import specific table into SMUS Project
    else:
        _grant_table_lf_permissions(lf_client,
                                    s3tables_client,
                                    table_bucket_arn,
                                    table_bucket_namespace,
                                    table_name,
                                    project_role_arn,
                                    execute_flag)

def byos3tb_main():
    args = _parse_args()
    session = boto3.Session()
    if (args.region):
        session = boto3.Session(region_name=args.region)
    lf_client = session.client('lakeformation')
    glue_client = session.client('glue')
    s3tables_client = session.client('s3tables')
    
    current_region = session.region_name
    s3_table_bucket_region = args.table_bucket_arn.split(':')[3]
    if current_region != s3_table_bucket_region:
        raise Exception(f"Error: Current region '{current_region}' does not match the region of the S3 Table Bucket '{s3_table_bucket_region}'. Please ensure the region is correct.")

    try:
        account_id = args.table_bucket_arn.split(':')[4]
        _add_lf_admin(lf_client, account_id, args.execute)
        _register_resource(lf_client, args.table_bucket_arn, args.iam_role_arn_lf_resource_register, args.execute)
        _create_glue_catalog(glue_client, args.table_bucket_arn, args.execute)
        _grant_s3_table_bucket_lf_permissions(lf_client, s3tables_client, args.project_role_arn, args.table_bucket_arn, args.table_bucket_namespace, args.table_name, args.execute)
    except Exception as e:
        print(f"An error occurred during import S3 Table Bucket process: {e}")
        raise
    if args.execute:
        print("Successfully imported S3 Table Bucket to SMUS project")

if __name__ == "__main__":
    byos3tb_main()
