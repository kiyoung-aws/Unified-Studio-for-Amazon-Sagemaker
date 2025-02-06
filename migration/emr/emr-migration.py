##Usage: python3 emr-migration.py --localPath <Local_path_To_EMR_workspace with e-BBBBBB> --repo <Sagemaker_studio_project_repoid> --emrStudioId es-AAAAAAA --emrWorkspaceId e-BBBBBB
## repo id can be found from your Sagemaker Unified Studio project's project overview page on the right side. Its in format datazone-yyyyyyyyyyy-dev

import os
import boto3
import argparse

code_commit = boto3.client('codecommit')

branch = "main"

def main():
    # Create an ArgumentParser object
    parser = argparse.ArgumentParser(description='Example script to demonstrate argument parsing')
    # Add arguments
    parser.add_argument('--localPath', type=str, help='Path to Local folder for EMR workgroup')
    parser.add_argument('--repo', type=str, help='Repo id for Sagemaker Studio Project')
    parser.add_argument('--emrStudioId', type=str, help='Id for EMR Studio. Format es-XXXX')
    parser.add_argument('--emrWorkspaceId', type=str, help='Id for EMR studio workspace. Format is e-YYYY')
    # Parse the arguments
    args = parser.parse_args()
    # Access the argument values
    global repo
    global local_folder
    global emr_studio_id
    global emr_workspace_id
    
    local_folder = args.localPath
    repo = args.repo
    emr_studio_id = args.emrStudioId
    emr_workspace_id = args.emrWorkspaceId
    # Print the argument values
    print(local_folder)
    print("The code commit repo is: " + "  ", repo)

if __name__ == '__main__':
    main()

#print(local_folder)
#print("The code commit repo is: " + "  ", repo)


emr_studio_id = "es-E8IMMZF7YFAC1OMV00OXH32R3"
emr_workspace_id = "e-6QUSSZXYJWG7BUQUJNLYG6AGI"

putFilesList = []

for (root, folders, files) in os.walk(local_folder):
        for file in files:
                    file_path = os.path.join(root, file)
                    print("Local file: " + file_path)
                    print("Uploading to: " + str(file_path).replace(local_folder, f'emr_notebooks/{emr_studio_id}/{emr_workspace_id}'))
                    with open(file_path, mode='r+b') as file_obj:
                        file_content = file_obj.read()
                        putFileEntry = {
                            'filePath': str(file_path).replace(local_folder, f'emr_notebooks/{emr_studio_id}/{emr_workspace_id}'),
                            'fileContent': file_content
                        }
                        putFilesList.append(putFileEntry)

parent_commit_id = code_commit.get_branch(repositoryName=repo, branchName=branch).get("branch").get("commitId")
code_commit.create_commit(
    repositoryName=repo,
    branchName=branch,
    parentCommitId=parent_commit_id,
    putFiles=putFilesList
)
