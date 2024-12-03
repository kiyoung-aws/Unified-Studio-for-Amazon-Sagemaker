# BringYourOwnRoleScript for SageMaker Unified Studio

A utility script for Bring Your Own IAM Role in SageMaker Unified Studio projects. This tool helps configure permissions and customize role assignments for SageMaker Unified Studio environments.

# Important Prerequisites and Considerations
## Resource Creation
The BYOR (Bring Your Own Role) role replacement functionality will prevent successful creation of new resources, including:
- Amazon EMR Cluster on EC2
- Amazon EMR Serverless
- Amazon Redshift Serverless
- Workflow environments
## Job Management
Before proceeding with the script execution:
1. Ensure all running jobs in your Project have been properly saved and completed
2. Verify that no jobs are currently in a mutating state
3. Any unsaved work may be lost during this process
## Resource Creation Status
To ensure successful script execution:
- Verify that no resource creation operations are currently in progress within your Unified Studio Project
- Any ongoing resource creation processes may interfere with and cause the script execution to fail

**Note:** Please review above requirements carefully before proceeding with the script execution.

## Prerequisites

Before using this script, ensure you have appropriate permissions configured through either an IAM role or IAM user.

### Required Permissions

1. Create a new IAM policy with the following permissions. Note: While this example uses "*" for `Resource`, consider restricting it according to your security requirements.
```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "DataZone",
            "Effect": "Allow",
            "Action": [
                "datazone:ListSubscriptions",
                "datazone:ListSubscriptionGrants",
                "datazone:UpdateSubscriptionTarget",
                "datazone:ListEnvironments",
                "datazone:DisassociateEnvironmentRole",
                "datazone:ListSubscriptionTargets",
                "datazone:AssociateEnvironmentRole",
                "datazone:ListSubscriptionRequests",
                "datazone:GetEnvironment",
                "datazone:CreateSubscriptionGrant",
                "datazone:DeleteSubscriptionGrant",
                "datazone:GetSubscriptionGrant"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "Glue",
            "Effect": "Allow",
            "Action": [
                "glue:GetDatabase",
                "glue:GetTable"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "IAM",
            "Effect": "Allow",
            "Action": [
                "iam:GetRole",
                "iam:UpdateAssumeRolePolicy",
                "iam:PassRole",
                "iam:ListRoleTags",
                "iam:ListAttachedRolePolicies",
                "iam:TagRole",
                "iam:ListRoles",
                "iam:AttachRolePolicy",
                "iam:PutRolePolicy",
                "iam:ListRolePolicies",
                "iam:GetRolePolicy",
                "iam:GetPolicy",
                "iam:GetPolicyVersion",
                "iam:CreatePolicyVersion"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "KMS",
            "Effect": "Allow",
            "Action": [
                "kms:Decrypt",
                "kms:GenerateDataKey",
                "kms:CreateGrant",
                "kms:ListGrants"
            ],
            "Resource": "*"
        },
        {
            "Sid": "Lakeformation",
            "Effect": "Allow",
            "Action": [
                "lakeformation:GrantPermissions",
                "lakeformation:ListLakeFormationOptIns",
                "lakeformation:ListPermissions",
                "lakeformation:CreateLakeFormationOptIn"
            ],
            "Resource": "*"
        },
        {
            "Sid": "SageMaker",
            "Effect": "Allow",
            "Action": [
                "sagemaker:ListDomains",
                "sagemaker:ListApps",
                "sagemaker:DeleteApp",
                "sagemaker:DescribeApp",
                "sagemaker:UpdateDomain"
            ],
            "Resource": "*"
        }
    ]
}
```
### Configuration Steps

1. Have the IAM policy as shown above ready
2. Attach the policy to your executor resource (IAM user or role)
3. Add the executor(IAM user or role) as the Domain's owner
4. Add the executor(IAM user or role) as the Project's owner, which you want to execute BYOR script on
5. Add the executor(IAM user or role) as LakeFormation Data lake administrators

### Authentication Setup

For information on configuring credentials to use the executor permissions, refer to the AWS CLI documentation on role configuration: https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-role.html

## Usage

### Location
In terminal, navigate to the directory containing `bring_your_own_role.py` before executing commands.

### Available Commands
#### Use Case 1: Replace SageMaker Unified Studio Project Role with your own Role
Replace the default project role with your custom role:
```
python3 bring_your_own_role.py use-your-own-role \
    --domain-id <SageMaker-Unified-Studio-Domain-Id> \
    --project-id <SageMaker-Unified-Studio-Project-Id> \
    --bring-in-role-arn <Custom-IAM-Role-Arn> \
    --region <region-code> \
    --endpoint <endpoint-url>
```
#### Use Case 2: Replace SageMaker Unified Studio Project Role with your own Role
```
python3 bring_your_own_role.py enhance-project-role \
    --domain-id <SageMaker-Unified-Studio-Domain-Id> \
    --project-id <SageMaker-Unified-Studio-Project-Id> \
    --bring-in-role-arn <Custom-IAM-Role-Arn> \
    --region <region-code> \
    --endpoint <endpoint-url>
```
### Important Notes
- Both commands will display a preview of proposed changes by default
- Add the `--execute` flag to apply the changes
- The `--region` and `--endpoint` parameters are optional and only required when necessary
