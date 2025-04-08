# S3 Table Bucket Import to SageMaker Unified Studio Project
 
This Python script allows you to import Tables created in S3 Table Bucket into a specified project in SageMaker Unified Studio, and then query imported tables using Athena or Redshift in your SMUS project.

## Script Details
This script (`bring_your_own_s3_table_bucket.py`) does the following work for you:
1. Add AWS managed role `AWSServiceRoleForRedshift` to `Data lake administrators`, with `ReadOnly` access
2. Register your S3 table(s) into LakeFormation
3. Create LakeFormation Catalog `s3tablescatalog` if you don't have one yet in current region
4. Grant SMUS Project User Role LakeFormation permissions of S3 table(s) you want to import

## Prerequisites
1. You need the following IAM permissions to execute the script for configuring permissions and customizing role assignments. If you have an existing IAM user or role with these permissions, use it for running the script. If not, then create a new IAM policy with the following permissions. The example below uses `*` for `Resource`, but you can restrict it according to your security requirements. These permissions are not needed once you complete executing the script:

```
{
    "Version": "2012-10-17",
    "Statement": [
        {
            "Sid": "Lakeformation",
            "Effect": "Allow",
            "Action": [
                "lakeformation:GrantPermissions",
                "lakeformation:GetDataAccess",
                "lakeformation:GetDataLakeSettings",
                "lakeformation:PutDataLakeSettings",
                "lakeformation:RegisterResource",
                "lakeformation:RegisterResourceWithPrivilegedAccess"
            ],
            "Resource": "*"
        },
        {
            "Sid": "IAM",
            "Effect": "Allow",
            "Action": [
                "iam:PassRole", # Required by LakeFormation RegisterResource
                "iam:GetRole"   # Required by LakeFormation RegisterResource
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "Glue",
            "Effect": "Allow",
            "Action": [
                "glue:PassConnection",
                "glue:CreateCatalog",
                "glue:GetTable"
            ],
            "Resource": [
                "*"
            ]
        },
        {
            "Sid": "S3TableBucket",
            "Effect": "Allow",
            "Action": [
                "s3tables:GetTable",
                "s3tables:ListTables"
            ],
            "Resource": [
                "*"
            ]
        }
    ]
}
```
2. Navigate to S3 Table buckets page in your account, ensure `Integration with AWS analytics services` is `Enabled` in the current region
3. Prepare an IAM role by following https://docs.aws.amazon.com/lake-formation/latest/dg/s3tables-catalog-prerequisites.html step3 and step4, it will be used as the input of `--iam-role-arn-lf-resource-register`
4. In the AWS Lake Formation console, grant grantable permissions of S3 table(s) you want to import, to your executor IAM user or role prepared in the 1st step, the easiest way is to add the executor IAM user or role as a Data Lake Administrator. This is required for the script to grant LakeFormation permissions to Project user role
5. Setup SMUS Project which you want to import your S3 Tables into
 
### Authentication Setup

For information on configuring credentials to use the executor permissions, refer to the AWS CLI documentation on role configuration: https://docs.aws.amazon.com/cli/v1/userguide/cli-configure-role.html
 
## Usage
 
### Location
Navigate to the directory containing `bring_your_own_s3_table_bucket.py` in the terminal before executing commands.
 
### Available Commands
 
#### Use Case example: Import an existing S3 table bucket's table into SageMaker Unified Studio Project
```
python3 bring_your_own_s3_table_bucket.py \
    --project-role-arn <Project role ARN> \
    --table-bucket-arn <S3 Table Bucket you want to bring in> \
    --table-bucket-namespace <S3 Table Bucket's namespace you want to bring in> \
    --table-name <S3 Table Bucket's table you want to bring in> \
    --region <region-code> \
    --iam-role-arn-lf-resource-register <IAM role arn with access to the S3 Tables> \
    --execute <True or False> 
```
 
### Important Notes
- This script currently only supports same-region and same-account use cases
- The `--region` parameter is optional and only required when necessary. If not specified, it defaults to AWS region specified in the CLI credentials config
- Add the `--execute` parameter to execute actual change, otherwise it will be executed in dry-run mode
- After executing the script, queries in Redshift may fail because your Redshift cluster is in deep pause, triggering a query command to wake it up will make it work properly


## Option 2
If you don't want to grant LakeFormation Administrator permission to the script executor, or if you don't want to use the script, please follow https://docs.aws.amazon.com/sagemaker-unified-studio/latest/userguide/lakehouse-s3-tables-integration.html to import S3 table into SMUS project through AWS Console.

### Note
With this approach the SMUS project Role would be set as SuperUser of `s3tablescatalog` Catalog.