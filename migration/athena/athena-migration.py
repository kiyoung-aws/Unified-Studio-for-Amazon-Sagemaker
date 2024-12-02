import argparse
import boto3
import os
import nbformat as nbf
import uuid

def migrate_queries(workgroup_name, repo, account_id, region):
    # Create boto3 clients with the specified region
    athena = boto3.client('athena', region_name=region)
    code_commit = boto3.client('codecommit', region_name=region)

    branch = "main"

    # Initialize an empty list to store all named query IDs
    all_named_query_ids = []

    # Paginate through all named queries
    paginator = athena.get_paginator('list_named_queries')
    for page in paginator.paginate(WorkGroup=workgroup_name):
        all_named_query_ids.extend(page['NamedQueryIds'])

    putFilesList = []
    migration_info = []  # List to store migration information

    # Process each named query
    for query_id in all_named_query_ids:
        query_result = athena.get_named_query(NamedQueryId=query_id)
        query_name = query_result['NamedQuery']['Name']
        query_string = query_result['NamedQuery']['QueryString']

        # Generate a UUID for this iteration
        new_uuid = str(uuid.uuid4())

        # Create the sqlnb file
        nb = nbf.read('template.sqlnb', as_version=4)
        code_cell = nbf.v4.new_code_cell(query_string)
        cell_metadata = {'isLimitOn': True, 'displayMode': 'maximized', 'width': 12}
        code_cell['metadata'] = cell_metadata
        nb['cells'].append(code_cell)
        nb['metadata']['title'] = query_name
        nb['metadata']['id'] = nb['metadata']['id'].replace('<uniqueid>', new_uuid)
        nb['metadata']['id'] = nb['metadata']['id'].replace('<region>', region)
        nb['metadata']['id'] = nb['metadata']['id'].replace('<aws-account-id>', account_id)

        # Write the sqlnb file
        with open(f'{query_name}.sqlnb', 'w') as f:
            nbf.write(nb, f)

        # Add the file to putFilesList
        with open(f'{query_name}.sqlnb', mode='r+b') as file_obj:
            file_content = file_obj.read()
        file_path = f'athena_saved_queries/{workgroup_name}/{query_name}.sqlnb'
        putFileEntry = {
            'filePath': file_path,
            'fileContent': file_content
        }
        putFilesList.append(putFileEntry)

        # Store migration info
        migration_info.append({
            'name': query_name,
            'query_id': query_id,
            'path': file_path
        })

        # Clean up the local file
        os.remove(f'{query_name}.sqlnb')

    # Perform a single commit with all files
    if putFilesList:
        parent_commit_id = code_commit.get_branch(repositoryName=repo, branchName=branch).get("branch").get("commitId")
        commit_response = code_commit.create_commit(
            repositoryName=repo,
            branchName=branch,
            parentCommitId=parent_commit_id,
            putFiles=putFilesList
        )
        
        # Check if commit was successful
        if 'commitId' in commit_response:
            print("Migration successful. Commit ID:", commit_response['commitId'])
            print("\nMigrated queries:")
            for info in migration_info:
                print(f"Name: {info['name']}")
                print(f"Query ID: {info['query_id']}")
                print(f"Migrated to: {info['path']}")
                print("---")
        else:
            print("Migration failed. No commit was made.")
    else:
        print("No queries to migrate.")

    print(f"Query migration process completed. Total queries migrated: {len(all_named_query_ids)}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Migrate Athena named queries to CodeCommit')
    parser.add_argument('--workgroup-name', type=str, required=True, help='Athena workgroup name')
    parser.add_argument('--repo', type=str, required=True, help='CodeCommit repository name')
    parser.add_argument('--account-id', type=str, required=True, help='AWS account ID')
    parser.add_argument('--region', type=str, required=True, help='AWS region')
    args = parser.parse_args()

    migrate_queries(args.workgroup_name, args.repo, args.account_id, args.region)
