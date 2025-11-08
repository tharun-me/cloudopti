# CloudOpti V2 - AWS Cost Monitoring & Optimization Tool

A comprehensive command-line tool to monitor AWS costs and optimize resources, similar to how Prowler works for security, but focused on cost optimization.

## Features

- 📊 **Cost Monitoring**: Collect last month's AWS bill with service-wise breakdown
- 🔍 **Resource Discovery**: Automatically discover EC2, EKS, S3, and VPC resources
- 📈 **CloudWatch Metrics**: Collect CPU, memory, disk, and network usage metrics
- 🔬 **Instance Analysis**: Analyze instance types, usage patterns, and optimization opportunities
- 💰 **Cost Optimization**: Get recommendations for right-sizing instances and reducing costs
- 📁 **Excel Reports**: Export detailed reports with multiple sheets per service
- 💡 **Smart Recommendations**: Actionable insights based on actual usage data

## Installation

### Quick Install (from PyPI - once published)

```bash
pip install cloudopti
```

### Install from GitHub

```bash
pip install git+https://github.com/testuser/cloudopti.git
```

### Install from Source

```bash
git clone https://github.com/testuser/cloudopti.git
cd cloudopti
pip install -e .
```

After installation, the `opti` command will be available globally:

```bash
opti aws
```

## Prerequisites

1. **Configure AWS credentials:**
   ```bash
   aws configure
   ```
   You'll need:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Output format (optional, recommended: `json`)

2. **Required AWS Permissions:**
   - **Cost Explorer API:**
     - `ce:GetCostAndUsage`
     - `ce:GetDimensionValues`
     - `ce:GetServiceCost`
   - **EC2:**
     - `ec2:DescribeInstances`
     - `ec2:DescribeVpcs`
     - `ec2:DescribeSubnets`
   - **EKS:**
     - `eks:ListClusters`
     - `eks:DescribeCluster`
     - `eks:ListNodegroups`
     - `eks:DescribeNodegroup`
   - **S3:**
     - `s3:ListAllMyBuckets`
     - `s3:ListBucket`
     - `s3:GetBucketLocation`
   - **CloudWatch:**
     - `cloudwatch:GetMetricStatistics`
     - `cloudwatch:ListMetrics`

## Usage

```bash
opti aws
```

This will:
1. Fetch last month's AWS costs
2. Discover all EC2, EKS, S3, and VPC resources
3. Collect CloudWatch metrics (CPU, memory, disk, network)
4. Analyze instance types and usage patterns
5. Generate optimization recommendations
6. Export comprehensive Excel report with multiple sheets

## Output

### On-Screen Output

- **Cost Summary**: Table showing costs per service
- **Resource Discovery**: List of discovered resources
- **Metrics Collection**: Progress of CloudWatch metrics collection
- **Analysis Results**: Instance analysis and recommendations
- **Cost-Saving Recommendations**: Actionable optimization suggestions

### Excel Report

The Excel file (`aws_cost_report_YYYYMMDD_HHMMSS.xlsx`) includes:

1. **Summary Sheet**: Cost breakdown by service and general recommendations
2. **EC2 Sheet**: Detailed analysis of each EC2 instance including:
   - Instance ID, Type, Region, State
   - vCPU, Memory specifications
   - CPU usage (average and maximum)
   - Monthly cost
   - Recommended instance type
   - Potential savings ($ and %)
   - Optimization recommendations
3. **EKS Sheet**: EKS cluster details including:
   - Cluster name, region, status, version
   - VPC ID
   - Node groups with instance types
   - CPU and memory utilization
4. **S3 Sheet**: S3 bucket analysis including:
   - Bucket name, region
   - Size and object count
   - Storage class distribution
   - Average metrics from CloudWatch
5. **VPC Sheet**: VPC details including:
   - VPC ID, region, CIDR block
   - State, default VPC status
   - Subnet count

## Example Output

```
📊 Fetching AWS costs from 2024-01-01 to 2024-02-01...

============================================================
💰 AWS COST REPORT - LAST MONTH
============================================================

+----------------------------------+------------+
| Service                          | Cost ($)   |
+==================================+============+
| Amazon Elastic Compute Cloud     | $125.50    |
| Amazon Simple Storage Service    | $45.20     |
| Amazon Relational Database...    | $89.30     |
| AWS Lambda                       | $12.10     |
+----------------------------------+------------+
| TOTAL                            | $272.10    |
+----------------------------------+------------+

============================================================
🔍 RESOURCE DISCOVERY
============================================================
🔍 Discovering EC2 instances...
  ✓ Found 5 EC2 instances
🔍 Discovering EKS clusters...
  ✓ Found 2 EKS clusters
🔍 Discovering S3 buckets...
  ✓ Found 8 S3 buckets
🔍 Discovering VPCs...
  ✓ Found 3 VPCs

============================================================
📈 COLLECTING RESOURCE METRICS
============================================================
📊 Collecting EC2 instance metrics...
  • i-1234567890abcdef0 (t3.large)... ✓
  • i-0987654321fedcba0 (m5.xlarge)... ✓
  ...

============================================================
🔬 ANALYZING RESOURCES
============================================================
🔍 Analyzing EC2 instances...
  • i-1234567890abcdef0 (t3.large)... ✓
  ...

============================================================
💡 COST-SAVING RECOMMENDATIONS
============================================================
  • EC2 costs $125.50. Consider stopping unused instances...
  • EC2 Instance Optimization: Potential savings of $45.20/month
    by right-sizing instances based on actual usage.
  • S3 costs $45.20. Review storage classes...
  ...

============================================================
✅ Report saved to: aws_cost_report_20241215_143022.xlsx
============================================================

📊 Report includes:
  • Summary sheet with cost breakdown
  • EC2 sheet with 5 instances and optimization recommendations
  • EKS sheet with 2 clusters
  • S3 sheet with 8 buckets
  • VPC sheet with 3 VPCs
============================================================
```

## Key Features Explained

### Resource Discovery
- Automatically discovers resources across all AWS regions
- Collects detailed information about each resource
- Handles permissions gracefully (continues if some regions fail)

### CloudWatch Metrics
- Collects 7 days of usage history
- Metrics include:
  - **EC2**: CPU utilization, network in/out, disk I/O
  - **EKS**: CPU and memory utilization
  - **S3**: Bucket size and object count

### Instance Analysis
- Analyzes actual usage vs. instance capacity
- Recommends optimal instance types based on:
  - CPU usage patterns
  - Memory requirements
  - Cost optimization potential
- Calculates potential savings in $ and %

### Cost Optimization
- Right-sizing recommendations based on actual usage
- Identifies over-provisioned instances
- Suggests downgrades for cost savings
- Flags underutilized resources

## Troubleshooting

**Error: "Failed to fetch AWS costs"**
- Check AWS credentials: `aws configure list`
- Verify Cost Explorer API is enabled in your AWS account
- Ensure you have the required permissions

**Error: "No module named 'boto3'"**
- Install dependencies: `pip install -r requirements.txt`

**Error: "UnauthorizedOperation"**
- Add missing IAM permissions for the specific service
- Check your IAM policy includes all required permissions

**Slow execution:**
- Resource discovery and metrics collection can take time
- The tool processes resources sequentially to avoid rate limits
- Large accounts with many resources will take longer

## Notes

- CloudWatch metrics require 7 days of data for accurate analysis
- Instance type recommendations are based on AWS pricing in us-east-1
- Actual savings may vary based on your region and usage patterns
- The tool respects AWS API rate limits
