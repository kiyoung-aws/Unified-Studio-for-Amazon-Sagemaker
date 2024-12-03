# Migrating from EMR Studio Notebooks to SageMaker Unified Studio for Data Processing

## Introduction

This guide provides step-by-step instructions and example script samples to help you migrate from Amazon EMR Studio to SageMaker Unified Studio for Data Processing. These resources will assist you in creating SageMaker Unified Studio for Data Processing projects in AWS Organization Member accounts.

## The migration process focuses on three key areas:

1. IAM Roles (Runtime Roles)
2. EMR Compute (Permission Changes)
3. EMR Studio (Notebooks)

## End-to-End Migration Flow

The following diagram illustrates the end-to-end migration process:

![End-to-End Migration Flow](https://github.com/aws/Unified-Studio-for-Amazon-Sagemaker/raw/main/migration/emr/img/e2e.png)

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Migration Steps](#migration-steps)
   - [2.1 IAM Roles Migration](#21-iam-roles-migration)
   - [2.2 EMR Compute Migration](#22-emr-compute-migration)
   - [2.3 Notebooks Migration](#23-notebooks-migration)
3. [Example Scripts](#example-scripts)
4. [Best Practices](#best-practices)
5. [Troubleshooting](#troubleshooting)
6. [Additional Resources](#additional-resources)

## Prerequisites

Before proceeding with migration, ensure you have:

- Understanding of [Amazon SageMaker Unified Studio](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/what-is-sagemaker-unified-studio.html)
- Access to a [domain](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/working-with-domains.html) and a project created in SageMaker Unified Studio (Refer to [Create a new project](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/create-new-project.html))
- Python, [boto3](https://pypi.org/project/boto3/) and [nbformat](https://pypi.org/project/nbformat/) installed on the machine where you'll execute migration steps
- [AWS Command Line Interface (AWS CLI)](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) installed/updated and configured on the machine where you'll execute migration steps
- The IAM User/Role performing the steps in this guide should have the following permissions:

```json
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Effect": "Allow",
            "Action": [
              "elasticmapreduce:GetClusterSessionCredentials"
            ],
            "Resource": "arn:aws:elasticmapreduce:<region>:<aws-account-id>:cluster/*"
        },
        {
            "Effect": "Allow",
            "Action": [
                "codecommit:GetBranch",
                "codecommit:CreateCommit"
            ],
            "Resource": "arn:aws:codecommit:<region>:<aws-account-id>:<repo-name>"
        },
        {
            "Effect": "Allow",
            "Action": [
                "datazone:ListConnections",
                "datazone:UpdateConnection"
            ],
            "Resource": "*"
        }
    ]
}
```
Step 1.2 below shows how to fetch the repo for the project. While the above sample uses "*” for some of the Resources, consider restricting it according to your security requirements.
- Add the IAM user/role as the [domain's owner](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/adminguide/user-management.html) and the [project's owner](https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/add-project-members.html) to be able to execute steps in this guide

## Migration Steps

### Step 1: IAM Roles (Runtime roles) - Bring your own role

**Stay Tuned**

### Step 2. Inventory Your EMR Studio Resources

- List all notebooks, workspaces, and associated data
- Identify and Copy Necessary Artifacts for Migration to MaxDome

From your SM Unified Studio Project notebook terminal, perform the following steps:

![Terminal](https://github.com/aws/Unified-Studio-for-Amazon-Sagemaker/blob/main/migration/emr/img/terminal.png))

a. Describe the EMR Studio by its ID to get the Default S3 location:

```bash
aws emr describe-studio --studio-id es-D5G4WREET32JMJ0W90RN686KH
```

Example output:

```
{
"Studio": {
"StudioId": "es-D5G4WREET32JMJ0W90RN686KH",
"StudioArn": "arn:aws:elasticmapreduce:us-west-2:XXXXXXXXXX:studio/es-D5G4WREET32JMJ0W90RN686KH",
"Name": "Studio_2",
"Description": "",
"AuthMode": "IAM",
"ServiceRole": "arn:aws:iam::XXXXXXXXXX:role/service-role/AmazonEMRStudio_ServiceRole_1728498237293",
"Url": "https://es-D5G4WREET32JMJ0W90RN686KH.emrstudio-prod.us-west-2.amazonaws.com",
"CreationTime": "2024-10-09T11:24:12.396000-07:00",
"DefaultS3Location": "s3://aws-emr-studio-XXXXXXXXXX-us-west-2/YYYYYYYYYY",
"Tags": [],
"IdcUserAssignment": "null"
}
}
```
b. List S3 default path to identify workspace folders:

NOTE: You might have more than one studio workspace. You have the option to migrate all notebooks across workspaces if your organization allows combining them together, or you can choose to migrate a specific workspace based on your needs. Consider your organization's policies and project requirements when deciding which workspaces to migrate.
If you decide to migrate all workspaces, you'll need to repeat the following steps for each workspace. If you're migrating a specific workspace, choose the appropriate workspace folder in the next step.

```
aws s3 ls s3://aws-emr-studio-XXXXXXXXXX-us-west-2/YYYYYYYYYY/
```

Example output:
```
                           PRE e-7QX2VHPYXESC65FUUC1WDT0E2/
                           PRE e-EU1V9IEQBY4ZWRIVS6GGH2MV7/
```
c. Download an entire sub-folder to your local machine:

```
aws s3 cp --recursive s3://aws-emr-studio-XXXXXXXXXX-us-west-2/YYYYYYYYYY/e-EU1V9IEQBY4ZWRIVS6GGH2MV7/ emr_workspace_files/e-EU1V9IEQBY4ZWRIVS6GGH2MV7
```

### Step 3. Migrate your notebooks

    * Export notebooks from EMR Studio
    * Import notebooks into SageMaker Unified Studio

a. Upload the entire folder to the MaxDome project's CodeCommit repository:

```
import os
import boto3

code_commit = boto3.client('codecommit')

repo = "src"
branch = "main"

local_folder = "/Users/<YOUR_USER_ID>/emr_workspace_files/e-EU1V9IEQBY4ZWRIVS6GGH2MV7"
emr_studio_id = "es-D5G4WREET32JMJ0W90RN686KH"
emr_workspace_id = "e-EU1V9IEQBY4ZWRIVS6GGH2MV7"

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
putFiles=putFilesList)
```

b. After running this script, go to the MaxDome portal and perform a git pull from the UI to see the imported files from the EMR workspace:

![Repo](https://github.com/aws/Unified-Studio-for-Amazon-Sagemaker/blob/main/migration/emr/img/repo.png)
![Repo2](https://github.com/aws/Unified-Studio-for-Amazon-Sagemaker/blob/main/migration/emr/img/repo2.png)
