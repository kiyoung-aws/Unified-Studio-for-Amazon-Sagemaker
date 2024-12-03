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

**Pending**

#### 1. Inventory Your EMR Studio Resources

- List all notebooks, workspaces, and associated data
- Identify and Copy Necessary Artifacts for Migration to MaxDome

From your MaxDome Project notebook terminal, perform the following steps:

a. Describe the EMR Studio by its ID to get the Default S3 location:

```bash
aws emr describe-studio --studio-id es-D5G4WREET32JMJ0W90RN686KH
