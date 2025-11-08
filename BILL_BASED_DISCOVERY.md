# Bill-Based Resource Discovery

## Overview

CloudOpti now discovers resources **strictly based on services that appear in your AWS bill**. It will only scan and analyze resources for services that have costs in your bill.

## How It Works

### 1. Bill Analysis

When you run `opti aws`, the tool:

1. **Fetches your AWS bill** from Cost Explorer API
2. **Analyzes each service** in the bill
3. **Maps service names** to resource discovery functions
4. **Only discovers resources** for services that appear in the bill

### 2. Service Mapping

The tool maps AWS service names from the bill to discovery functions:

| Bill Service Name | Discovery Key | Resources Discovered |
|------------------|---------------|---------------------|
| Amazon Elastic Compute Cloud - Compute | EC2 | EC2 Instances |
| Amazon Relational Database Service | RDS | RDS Instances |
| Amazon Simple Storage Service | S3 | S3 Buckets |
| Amazon Elastic Container Service for Kubernetes | EKS | EKS Clusters |
| Amazon Virtual Private Cloud | VPC | VPCs |
| AWS Lambda | Lambda | Lambda Functions |
| Amazon DynamoDB | DynamoDB | DynamoDB Tables |
| Amazon Elastic Load Balancing | ELB | Load Balancers |

### 3. Discovery Process

```
Bill → Service Names → Map to Discovery Keys → Discover Resources → Analyze → Excel Report
```

## Example

### Your Bill Contains:
- Amazon Elastic Container Service for Kubernetes: $258.17
- Amazon Relational Database Service: $228.57
- Amazon Elastic Compute Cloud - Compute: $122.37
- Amazon Virtual Private Cloud: $49.16
- Tax: $127.47
- AWS Support (Business): $0.50

### What Gets Discovered:
✅ **EKS** - Will discover EKS clusters  
✅ **RDS** - Will discover RDS instances  
✅ **EC2** - Will discover EC2 instances  
✅ **VPC** - Will discover VPCs  
❌ **Tax** - Skipped (not a resource)  
❌ **AWS Support** - Skipped (not a resource)

### What Gets Skipped:
- Services not in the bill (even if they exist in your account)
- Non-resource services (Tax, Support, etc.)
- Services without discovery support

## Output

### Console Output

```
============================================================
🔍 ANALYZING BILL FOR DISCOVERABLE SERVICES
============================================================

✅ Discoverable services in bill:
  • Amazon Elastic Container Service for Kubernetes ($258.17) → Will discover EKS resources
  • Amazon Relational Database Service ($228.57) → Will discover RDS resources
  • Amazon Elastic Compute Cloud - Compute ($122.37) → Will discover EC2 resources
  • Amazon Virtual Private Cloud ($49.16) → Will discover VPC resources

⚠️  Services in bill without resource discovery:
  • Tax ($127.47) - No resource discovery available
  • AWS Support (Business) ($0.50) - No resource discovery available

📋 Will discover resources for: EKS, RDS, EC2, VPC

============================================================
🔍 RESOURCE DISCOVERY (Based on Bill)
============================================================

📋 Services in bill that will be analyzed:
  • Amazon Elastic Container Service for Kubernetes ($258.17) → EKS
  • Amazon Relational Database Service ($228.57) → RDS
  • Amazon Elastic Compute Cloud - Compute ($122.37) → EC2
  • Amazon Virtual Private Cloud ($49.16) → VPC

🔍 Discovering resources for: EKS, RDS, EC2, VPC
...
```

### Excel Report

The Excel report will **only include sheets** for services that were discovered (based on the bill):

- ✅ Summary sheet (always included)
- ✅ EKS sheet (if EKS in bill)
- ✅ RDS sheet (if RDS in bill)
- ✅ EC2 sheet (if EC2 in bill)
- ✅ VPC sheet (if VPC in bill)
- ❌ Lambda sheet (only if Lambda in bill)
- ❌ DynamoDB sheet (only if DynamoDB in bill)

## Benefits

1. **Faster Execution**: Only scans services that matter
2. **Focused Analysis**: Analyzes only what you're paying for
3. **Relevant Reports**: Excel sheets only for services in your bill
4. **Clear Visibility**: Shows which services can/cannot be analyzed

## Adding New Services

To add resource discovery for a new service:

1. Add service mapping in `cloudopti/service_mapper.py`:
   ```python
   'Service Name in Bill': 'DiscoveryKey',
   ```

2. Add discovery function in `cloudopti/resource_discovery.py`:
   ```python
   def discover_new_service(self):
       # Discovery logic
   ```

3. Add to `discover_all_resources()`:
   ```python
   if 'DiscoveryKey' in services_to_discover:
       resources['DiscoveryKey'] = self.discover_new_service()
   ```

4. Add Excel sheet in `cloudopti/excel_exporter.py`:
   ```python
   if resources.get('DiscoveryKey'):
       self.create_new_service_sheet(wb, resources['DiscoveryKey'])
   ```

## Troubleshooting

### "No discoverable services found in the bill"

This means:
- All services in your bill are non-resource services (Tax, Support, etc.)
- OR all services in your bill don't have discovery support yet

**Solution**: Check which services are in your bill and ensure they're mapped in `SERVICE_MAP`.

### Service in bill but not discovered

**Possible reasons**:
1. Service name doesn't match exactly (check SERVICE_MAP)
2. Service doesn't have discovery function yet
3. Service is in non-resource list (Tax, Support, etc.)

**Solution**: Check the console output - it will show which services cannot be discovered.

## Summary

✅ **Bill-based discovery** - Only discovers what's in your bill  
✅ **Smart mapping** - Maps bill services to resources  
✅ **Focused analysis** - Analyzes only relevant services  
✅ **Clear reporting** - Shows what can/cannot be analyzed  
✅ **Efficient** - Skips services not in bill

