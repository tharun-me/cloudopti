"""Service Mapper - Maps AWS service names to resource discovery functions"""

# Map AWS service names from Cost Explorer to resource discovery keys
SERVICE_MAP = {
    # EC2
    'Amazon Elastic Compute Cloud - Compute': 'EC2',
    'EC2 - Other': 'EC2',
    'EC2-Other': 'EC2',
    
    # EKS
    'Amazon Elastic Container Service for Kubernetes': 'EKS',
    'Amazon EKS': 'EKS',
    
    # S3
    'Amazon Simple Storage Service': 'S3',
    
    # RDS
    'Amazon Relational Database Service': 'RDS',
    
    # VPC
    'Amazon Virtual Private Cloud': 'VPC',
    
    # Lambda
    'AWS Lambda': 'Lambda',
    
    # DynamoDB
    'Amazon DynamoDB': 'DynamoDB',
    
    # ELB
    'Amazon Elastic Load Balancing': 'ELB',
    
    # CloudWatch
    'AmazonCloudWatch': 'CloudWatch',
    
    # Route 53
    'Amazon Route 53': 'Route53',
    
    # Systems Manager
    'AWS Systems Manager': 'SystemsManager',
    
    # Secrets Manager
    'AWS Secrets Manager': 'SecretsManager',
    
    # GuardDuty
    'Amazon GuardDuty': 'GuardDuty',
}


def get_services_to_discover(costs_by_service):
    """Get list of services to discover based on costs in the bill, ordered by cost (highest first)"""
    services_to_discover = []  # Use list to preserve order
    service_mapping = {}  # Track which bill services map to which discovery keys
    seen_keys = set()  # Track which discovery keys we've already added
    
    # Services that don't have discoverable resources
    non_resource_services = [
        'Tax', 
        'AWS Support (Business)', 
        'AWS Support (Developer)', 
        'AWS Support (Enterprise)', 
        'AWS Support (Basic)'
    ]
    
    # Sort services by cost (highest first) to match bill order
    sorted_services = sorted(costs_by_service.items(), key=lambda x: x[1], reverse=True)
    
    for service_name, cost in sorted_services:
        # Skip non-resource services
        if service_name in non_resource_services:
            continue
        
        # Map service name to discovery key
        discovery_key = SERVICE_MAP.get(service_name)
        if discovery_key:
            # Track the mapping
            if discovery_key not in service_mapping:
                service_mapping[discovery_key] = []
            service_mapping[discovery_key].append({
                'bill_name': service_name,
                'cost': cost
            })
            
            # Add to list in order (only once per discovery key)
            if discovery_key not in seen_keys:
                services_to_discover.append(discovery_key)
                seen_keys.add(discovery_key)
    
    return services_to_discover, service_mapping


def get_service_name_from_bill(discovery_key):
    """Get the service name as it appears in the bill"""
    # Reverse lookup
    for bill_name, key in SERVICE_MAP.items():
        if key == discovery_key:
            return bill_name
    return None

