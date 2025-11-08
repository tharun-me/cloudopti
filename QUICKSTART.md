# Quick Start Guide

## Installation

1. **Install the package:**
   ```bash
   pip install -e .
   ```

2. **Configure AWS credentials:**
   ```bash
   aws configure
   ```
   
   You'll need:
   - AWS Access Key ID
   - AWS Secret Access Key
   - Default region (e.g., `us-east-1`)
   - Output format (optional, recommended: `json`)

3. **Required AWS Permissions:**
   Make sure your AWS credentials have these permissions:
   - `ce:GetCostAndUsage` (Cost Explorer API)
   - `ce:GetDimensionValues`
   - `ce:GetServiceCost`

## Usage

Simply run:
```bash
opti aws
```

## What It Does

1. ✅ Fetches last month's AWS costs
2. ✅ Breaks down costs by service (EC2, S3, RDS, Lambda, etc.)
3. ✅ Displays a clean table on screen
4. ✅ Saves report to Excel file (`aws_cost_report_YYYYMMDD_HHMMSS.xlsx`)
5. ✅ Provides cost-saving recommendations

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
💡 COST-SAVING RECOMMENDATIONS
============================================================
  • EC2 costs $125.50. Consider stopping unused instances...
  • S3 costs $45.20. Review storage classes...
  • ...

============================================================
✅ Report saved to: aws_cost_report_20241215_143022.xlsx
============================================================
```

## Troubleshooting

**Error: "Failed to fetch AWS costs"**
- Check AWS credentials: `aws configure list`
- Verify Cost Explorer API is enabled in your AWS account
- Ensure you have the required permissions

**Error: "No module named 'boto3'"**
- Install dependencies: `pip install -r requirements.txt`

