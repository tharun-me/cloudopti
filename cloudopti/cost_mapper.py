"""Cost Mapper - Map actual costs from bill to individual resources"""

import boto3
from datetime import datetime, timedelta


class CostMapper:
    """Map actual costs from Cost Explorer to individual resources"""
    
    def __init__(self):
        """Initialize Cost Explorer client"""
        self.ce_client = boto3.client('ce')
    
    def get_last_month_dates(self):
        """Get start and end dates for last month"""
        today = datetime.now()
        first_day_current = today.replace(day=1)
        last_day_last_month = first_day_current - timedelta(days=1)
        first_day_last_month = last_day_last_month.replace(day=1)
        
        start_date = first_day_last_month.strftime('%Y-%m-%d')
        end_date = (last_day_last_month + timedelta(days=1)).strftime('%Y-%m-%d')
        
        return start_date, end_date
    
    def get_ec2_instance_costs(self, instance_ids, regions):
        """Get actual costs for EC2 instances"""
        start_date, end_date = self.get_last_month_dates()
        
        instance_costs = {}
        
        # Group by region for efficiency
        for region in set(regions):
            region_instances = [inst_id for inst_id, reg in zip(instance_ids, regions) if reg == region]
            
            if not region_instances:
                continue
            
            try:
                # Get costs grouped by instance ID
                response = self.ce_client.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date,
                        'End': end_date
                    },
                    Granularity='MONTHLY',
                    Metrics=['UnblendedCost'],
                    Filter={
                        'And': [
                            {
                                'Dimensions': {
                                    'Key': 'SERVICE',
                                    'Values': ['Amazon Elastic Compute Cloud - Compute']
                                }
                            },
                            {
                                'Dimensions': {
                                    'Key': 'REGION',
                                    'Values': [region]
                                }
                            }
                        ]
                    },
                    GroupBy=[
                        {
                            'Type': 'DIMENSION',
                            'Key': 'RESOURCE_ID'
                        }
                    ]
                )
                
                for result in response.get('ResultsByTime', []):
                    for group in result.get('Groups', []):
                        resource_id = group['Keys'][0]
                        amount = float(group['Metrics']['UnblendedCost']['Amount'])
                        
                        # Check if this resource ID matches any of our instances
                        for inst_id in region_instances:
                            if inst_id in resource_id or resource_id in inst_id:
                                instance_costs[inst_id] = amount
                                break
            except Exception:
                # If detailed cost per instance fails, distribute service cost evenly
                pass
        
        return instance_costs
    
    def get_rds_instance_costs(self, db_instance_ids, regions):
        """Get actual costs for RDS instances"""
        start_date, end_date = self.get_last_month_dates()
        
        rds_costs = {}
        
        for region in set(regions):
            region_instances = [db_id for db_id, reg in zip(db_instance_ids, regions) if reg == region]
            
            if not region_instances:
                continue
            
            try:
                response = self.ce_client.get_cost_and_usage(
                    TimePeriod={
                        'Start': start_date,
                        'End': end_date
                    },
                    Granularity='MONTHLY',
                    Metrics=['UnblendedCost'],
                    Filter={
                        'And': [
                            {
                                'Dimensions': {
                                    'Key': 'SERVICE',
                                    'Values': ['Amazon Relational Database Service']
                                }
                            },
                            {
                                'Dimensions': {
                                    'Key': 'REGION',
                                    'Values': [region]
                                }
                            }
                        ]
                    },
                    GroupBy=[
                        {
                            'Type': 'DIMENSION',
                            'Key': 'RESOURCE_ID'
                        }
                    ]
                )
                
                for result in response.get('ResultsByTime', []):
                    for group in result.get('Groups', []):
                        resource_id = group['Keys'][0]
                        amount = float(group['Metrics']['UnblendedCost']['Amount'])
                        
                        for db_id in region_instances:
                            if db_id in resource_id or resource_id in db_id:
                                rds_costs[db_id] = amount
                                break
            except Exception:
                pass
        
        return rds_costs
    
    def get_s3_bucket_costs(self, bucket_names):
        """Get actual costs for S3 buckets"""
        start_date, end_date = self.get_last_month_dates()
        
        bucket_costs = {}
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                Filter={
                    'Dimensions': {
                        'Key': 'SERVICE',
                        'Values': ['Amazon Simple Storage Service']
                    }
                },
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'RESOURCE_ID'
                    }
                ]
            )
            
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    resource_id = group['Keys'][0]
                    amount = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    # S3 resource IDs are bucket names
                    for bucket_name in bucket_names:
                        if bucket_name in resource_id or resource_id == bucket_name:
                            bucket_costs[bucket_name] = amount
                            break
        except Exception:
            pass
        
        return bucket_costs
    
    def get_service_cost_distribution(self, service_name, total_cost, resource_count):
        """Distribute service cost evenly among resources if detailed costs unavailable"""
        if resource_count == 0:
            return {}
        
        cost_per_resource = total_cost / resource_count
        return {i: cost_per_resource for i in range(resource_count)}
    
    def map_costs_to_resources(self, resources, costs_by_service):
        """Map actual costs to all resources"""
        resource_costs = {}
        
        # EC2 costs
        if resources.get('EC2'):
            instance_ids = [inst['InstanceId'] for inst in resources['EC2']]
            regions = [inst['Region'] for inst in resources['EC2']]
            ec2_costs = self.get_ec2_instance_costs(instance_ids, regions)
            
            # If detailed costs not available, distribute service cost
            if not ec2_costs and 'Amazon Elastic Compute Cloud - Compute' in costs_by_service:
                ec2_total = costs_by_service['Amazon Elastic Compute Cloud - Compute']
                cost_per_instance = ec2_total / len(instance_ids) if instance_ids else 0
                ec2_costs = {inst_id: cost_per_instance for inst_id in instance_ids}
            
            resource_costs['EC2'] = ec2_costs
        
        # RDS costs
        if resources.get('RDS'):
            db_ids = [db['DBInstanceIdentifier'] for db in resources['RDS']]
            regions = [db['Region'] for db in resources['RDS']]
            rds_costs = self.get_rds_instance_costs(db_ids, regions)
            
            if not rds_costs and 'Amazon Relational Database Service' in costs_by_service:
                rds_total = costs_by_service['Amazon Relational Database Service']
                cost_per_db = rds_total / len(db_ids) if db_ids else 0
                rds_costs = {db_id: cost_per_db for db_id in db_ids}
            
            resource_costs['RDS'] = rds_costs
        
        # S3 costs
        if resources.get('S3'):
            bucket_names = [bucket['BucketName'] for bucket in resources['S3']]
            s3_costs = self.get_s3_bucket_costs(bucket_names)
            
            if not s3_costs and 'Amazon Simple Storage Service' in costs_by_service:
                s3_total = costs_by_service['Amazon Simple Storage Service']
                cost_per_bucket = s3_total / len(bucket_names) if bucket_names else 0
                s3_costs = {bucket_name: cost_per_bucket for bucket_name in bucket_names}
            
            resource_costs['S3'] = s3_costs
        
        # EKS costs (distribute service cost)
        if resources.get('EKS') and 'Amazon Elastic Container Service for Kubernetes' in costs_by_service:
            eks_total = costs_by_service['Amazon Elastic Container Service for Kubernetes']
            cluster_names = [cluster['ClusterName'] for cluster in resources['EKS']]
            cost_per_cluster = eks_total / len(cluster_names) if cluster_names else 0
            resource_costs['EKS'] = {name: cost_per_cluster for name in cluster_names}
        
        return resource_costs

