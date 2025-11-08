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
    """Get list of services to discover based on costs"""
    services_to_discover = set()
    
    for service_name in costs_by_service.keys():
        # Skip non-resource services
        if service_name in ['Tax', 'AWS Support (Business)', 'AWS Support (Developer)', 
                           'AWS Support (Enterprise)', 'AWS Support (Basic)']:
            continue
        
        # Map service name to discovery key
        discovery_key = SERVICE_MAP.get(service_name)
        if discovery_key:
            services_to_discover.add(discovery_key)
    
    return list(services_to_discover)


def get_service_name_from_bill(discovery_key):
    """Get the service name as it appears in the bill"""
    # Reverse lookup
    for bill_name, key in SERVICE_MAP.items():
        if key == discovery_key:
            return bill_name
    return None

