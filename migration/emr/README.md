# Migrating from EMR Studio Notebooks to SageMaker Unified Studio for Data Processing

## Introduction

This guide provides step-by-step instructions and example script samples to help you migrate from Amazon EMR Studio to SageMaker Unified Studio for Data Processing. These resources will assist you in creating SageMaker Unified Studio for Data Processing projects in AWS Organization Member accounts.

## The migration process focuses on three key areas:

1. IAM Roles (Runtime Roles)
2. EMR Compute (Permission Changes)
3. EMR Studio (Notebooks)

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

Before beginning the migration process from EMR Studio to SageMaker Unified Studio for Data Processing, ensure you have the following:

### Access and Permissions
- [ ] Access to both EMR Studio and SageMaker Unified Studio for Data Processing
- [ ] Necessary IAM permissions in your AWS account for both services

### AWS Environment Setup
- [ ] AWS CLI installed and configured with appropriate credentials
- [ ] Python environment with boto3 library installed (version X.X or higher)

### Data Preparation
- [ ] All EMR Studio notebooks and associated data backed up
- [ ] Inventory of all EMR Studio resources (notebooks, clusters, configurations)

### EMR Configuration
- [ ] For EMR on EC2: Clusters with GCSC (GetClusterSessionCredentials) API enabled via Security Configuration
- [ ] For EMR Serverless: Runtime roles identified and documented

### SageMaker Studio Readiness
- [ ] SageMaker domain and user profile set up
- [ ] Familiarity with SageMaker Studio interface and basic operations

### Network and Security
- [ ] VPC and security group configurations reviewed and prepared for MaxDome
- [ ] Any required VPC endpoints for SageMaker and related services set up

### Additional Tools
- [ ] Git repository for version control of notebooks (recommended)
- [ ] Any specialized libraries or dependencies used in EMR Studio identified for reinstallation in MaxDome

### Documentation
- [ ] EMR Studio workflow processes documented for reference during migration

By ensuring all these prerequisites are met, you'll be well-prepared to begin the migration process to SageMaker Unified Studio for Data Processing. The following sections will guide you through the step-by-step migration process, provide example scripts, and offer best practices and troubleshooting tips.
