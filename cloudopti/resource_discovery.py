"""AWS Resource Discovery - Collects details about EC2, EKS, S3, VPC resources"""

import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


class ResourceDiscovery:
    """Discover and collect details about AWS resources"""
    
    def __init__(self):
        """Initialize AWS clients"""
        # Get default region from AWS config or use us-east-1 as fallback
        session = boto3.Session()
        default_region = session.region_name or 'us-east-1'
        
        # S3 doesn't require a region, but others do
        self.s3_client = boto3.client('s3')
        self.default_region = default_region
        self.regions = self._get_regions()
    
    def _get_regions(self):
        """Get list of available AWS regions"""
        try:
            ec2 = boto3.client('ec2', region_name='us-east-1')
            response = ec2.describe_regions()
            return [region['RegionName'] for region in response['Regions']]
        except Exception:
            # Fallback to common regions
            return ['us-east-1', 'us-west-2', 'eu-west-1', 'ap-southeast-1']
    
    def discover_ec2_instances(self):
        """Discover all EC2 instances across regions"""
        print("🔍 Discovering EC2 instances...")
        instances = []
        
        for region in self.regions:
            try:
                ec2 = boto3.client('ec2', region_name=region)
                response = ec2.describe_instances()
                
                for reservation in response.get('Reservations', []):
                    for instance in reservation.get('Instances', []):
                        if instance['State']['Name'] in ['running', 'stopped']:
                            instance_info = {
                                'InstanceId': instance['InstanceId'],
                                'InstanceType': instance.get('InstanceType', 'N/A'),
                                'State': instance['State']['Name'],
                                'Region': region,
                                'LaunchTime': instance.get('LaunchTime', datetime.now()),
                                'Tags': {tag['Key']: tag['Value'] for tag in instance.get('Tags', [])},
                                'VpcId': instance.get('VpcId', 'N/A'),
                                'SubnetId': instance.get('SubnetId', 'N/A'),
                                'Platform': instance.get('Platform', 'linux/unix'),
                                'ImageId': instance.get('ImageId', 'N/A'),
                            }
                            instances.append(instance_info)
            except ClientError as e:
                if e.response['Error']['Code'] != 'UnauthorizedOperation':
                    continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(instances)} EC2 instances")
        return instances
    
    def discover_eks_clusters(self):
        """Discover all EKS clusters across regions"""
        print("🔍 Discovering EKS clusters...")
        clusters = []
        
        for region in self.regions:
            try:
                eks = boto3.client('eks', region_name=region)
                response = eks.list_clusters()
                
                for cluster_name in response.get('clusters', []):
                    try:
                        cluster_detail = eks.describe_cluster(name=cluster_name)
                        cluster_info = cluster_detail['cluster']
                        
                        cluster_data = {
                            'ClusterName': cluster_info['name'],
                            'Region': region,
                            'Status': cluster_info.get('status', 'N/A'),
                            'Version': cluster_info.get('version', 'N/A'),
                            'CreatedAt': cluster_info.get('createdAt', datetime.now()),
                            'Endpoint': cluster_info.get('endpoint', 'N/A'),
                            'VpcId': cluster_info.get('resourcesVpcConfig', {}).get('vpcId', 'N/A'),
                            'NodeGroups': []
                        }
                        
                        # Get node groups
                        try:
                            node_groups = eks.list_nodegroups(clusterName=cluster_name)
                            for ng_name in node_groups.get('nodegroups', []):
                                ng_detail = eks.describe_nodegroup(
                                    clusterName=cluster_name,
                                    nodegroupName=ng_name
                                )
                                ng_info = ng_detail['nodegroup']
                                cluster_data['NodeGroups'].append({
                                    'Name': ng_info['nodegroupName'],
                                    'InstanceType': ng_info.get('instanceTypes', ['N/A'])[0],
                                    'DesiredSize': ng_info.get('scalingConfig', {}).get('desiredSize', 0),
                                    'MinSize': ng_info.get('scalingConfig', {}).get('minSize', 0),
                                    'MaxSize': ng_info.get('scalingConfig', {}).get('maxSize', 0),
                                    'Status': ng_info.get('status', 'N/A'),
                                })
                        except Exception:
                            pass
                        
                        clusters.append(cluster_data)
                    except Exception:
                        continue
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(clusters)} EKS clusters")
        return clusters
    
    def discover_s3_buckets(self):
        """Discover all S3 buckets"""
        print("🔍 Discovering S3 buckets...")
        buckets = []
        
        try:
            # S3 client doesn't need region for list_buckets
            s3_client = boto3.client('s3')
            response = s3_client.list_buckets()
            
            for bucket in response.get('Buckets', []):
                bucket_name = bucket['Name']
                bucket_data = {
                    'BucketName': bucket_name,
                    'CreationDate': bucket.get('CreationDate', datetime.now()),
                    'Region': 'us-east-1',  # Default, will try to get actual region
                    'Size': 0,
                    'ObjectCount': 0,
                    'StorageClass': {}
                }
                
                # Try to get bucket location and details
                try:
                    location = s3_client.get_bucket_location(Bucket=bucket_name)
                    bucket_data['Region'] = location.get('LocationConstraint') or 'us-east-1'
                except Exception:
                    pass
                
                # Get bucket size and object count (this can be slow for large buckets)
                try:
                    paginator = s3_client.get_paginator('list_objects_v2')
                    total_size = 0
                    total_objects = 0
                    storage_classes = {}
                    
                    for page in paginator.paginate(Bucket=bucket_name):
                        for obj in page.get('Contents', []):
                            total_size += obj.get('Size', 0)
                            total_objects += 1
                            storage_class = obj.get('StorageClass', 'STANDARD')
                            storage_classes[storage_class] = storage_classes.get(storage_class, 0) + obj.get('Size', 0)
                    
                    bucket_data['Size'] = total_size
                    bucket_data['ObjectCount'] = total_objects
                    bucket_data['StorageClass'] = storage_classes
                except Exception:
                    pass
                
                buckets.append(bucket_data)
        except Exception as e:
            print(f"  ⚠ Error discovering S3 buckets: {str(e)}")
        
        print(f"  ✓ Found {len(buckets)} S3 buckets")
        return buckets
    
    def discover_vpcs(self):
        """Discover all VPCs across regions"""
        print("🔍 Discovering VPCs...")
        vpcs = []
        
        for region in self.regions:
            try:
                ec2 = boto3.client('ec2', region_name=region)
                response = ec2.describe_vpcs()
                
                for vpc in response.get('Vpcs', []):
                    vpc_data = {
                        'VpcId': vpc['VpcId'],
                        'Region': region,
                        'CidrBlock': vpc.get('CidrBlock', 'N/A'),
                        'State': vpc.get('State', 'N/A'),
                        'IsDefault': vpc.get('IsDefault', False),
                        'Tags': {tag['Key']: tag['Value'] for tag in vpc.get('Tags', [])},
                    }
                    
                    # Get subnets
                    try:
                        subnets = ec2.describe_subnets(Filters=[{'Name': 'vpc-id', 'Values': [vpc['VpcId']]}])
                        vpc_data['SubnetCount'] = len(subnets.get('Subnets', []))
                    except Exception:
                        vpc_data['SubnetCount'] = 0
                    
                    vpcs.append(vpc_data)
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(vpcs)} VPCs")
        return vpcs
    
    def discover_rds_instances(self):
        """Discover all RDS instances across regions"""
        print("🔍 Discovering RDS instances...")
        instances = []
        
        for region in self.regions:
            try:
                rds = boto3.client('rds', region_name=region)
                response = rds.describe_db_instances()
                
                for db_instance in response.get('DBInstances', []):
                    instance_data = {
                        'DBInstanceIdentifier': db_instance['DBInstanceIdentifier'],
                        'DBInstanceClass': db_instance.get('DBInstanceClass', 'N/A'),
                        'Engine': db_instance.get('Engine', 'N/A'),
                        'EngineVersion': db_instance.get('EngineVersion', 'N/A'),
                        'Region': region,
                        'Status': db_instance.get('DBInstanceStatus', 'N/A'),
                        'MultiAZ': db_instance.get('MultiAZ', False),
                        'StorageType': db_instance.get('StorageType', 'N/A'),
                        'AllocatedStorage': db_instance.get('AllocatedStorage', 0),
                        'VpcId': db_instance.get('DBSubnetGroup', {}).get('VpcId', 'N/A'),
                        'CreatedAt': db_instance.get('InstanceCreateTime', datetime.now()),
                    }
                    instances.append(instance_data)
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(instances)} RDS instances")
        return instances
    
    def discover_all_resources(self, services_to_discover=None):
        """Discover all resources based on services in the bill"""
        print("\n" + "="*60)
        print("🔍 RESOURCE DISCOVERY")
        print("="*60)
        
        # If no services specified, discover all
        if services_to_discover is None:
            services_to_discover = ['EC2', 'EKS', 'S3', 'VPC', 'RDS']
        
        resources = {}
        
        if 'EC2' in services_to_discover:
            resources['EC2'] = self.discover_ec2_instances()
        
        if 'EKS' in services_to_discover:
            resources['EKS'] = self.discover_eks_clusters()
        
        if 'S3' in services_to_discover:
            resources['S3'] = self.discover_s3_buckets()
        
        if 'VPC' in services_to_discover:
            resources['VPC'] = self.discover_vpcs()
        
        if 'RDS' in services_to_discover:
            resources['RDS'] = self.discover_rds_instances()
        
        if 'Lambda' in services_to_discover:
            resources['Lambda'] = self.discover_lambda_functions()
        
        if 'DynamoDB' in services_to_discover:
            resources['DynamoDB'] = self.discover_dynamodb_tables()
        
        if 'ELB' in services_to_discover:
            resources['ELB'] = self.discover_load_balancers()
        
        return resources
    
    def discover_lambda_functions(self):
        """Discover all Lambda functions across regions"""
        print("🔍 Discovering Lambda functions...")
        functions = []
        
        for region in self.regions:
            try:
                lambda_client = boto3.client('lambda', region_name=region)
                response = lambda_client.list_functions()
                
                for func in response.get('Functions', []):
                    func_data = {
                        'FunctionName': func['FunctionName'],
                        'Runtime': func.get('Runtime', 'N/A'),
                        'MemorySize': func.get('MemorySize', 0),
                        'Timeout': func.get('Timeout', 0),
                        'Region': region,
                        'LastModified': func.get('LastModified', datetime.now()),
                        'CodeSize': func.get('CodeSize', 0),
                    }
                    functions.append(func_data)
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(functions)} Lambda functions")
        return functions
    
    def discover_dynamodb_tables(self):
        """Discover all DynamoDB tables across regions"""
        print("🔍 Discovering DynamoDB tables...")
        tables = []
        
        for region in self.regions:
            try:
                dynamodb = boto3.client('dynamodb', region_name=region)
                response = dynamodb.list_tables()
                
                for table_name in response.get('TableNames', []):
                    try:
                        table_detail = dynamodb.describe_table(TableName=table_name)
                        table_info = table_detail['Table']
                        
                        table_data = {
                            'TableName': table_name,
                            'Region': region,
                            'Status': table_info.get('TableStatus', 'N/A'),
                            'ItemCount': table_info.get('ItemCount', 0),
                            'TableSizeBytes': table_info.get('TableSizeBytes', 0),
                            'BillingMode': table_info.get('BillingModeSummary', {}).get('BillingMode', 'N/A'),
                        }
                        tables.append(table_data)
                    except Exception:
                        continue
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(tables)} DynamoDB tables")
        return tables
    
    def discover_load_balancers(self):
        """Discover all load balancers across regions"""
        print("🔍 Discovering Load Balancers...")
        load_balancers = []
        
        for region in self.regions:
            try:
                elbv2 = boto3.client('elbv2', region_name=region)
                response = elbv2.describe_load_balancers()
                
                for lb in response.get('LoadBalancers', []):
                    lb_data = {
                        'LoadBalancerName': lb.get('LoadBalancerName', lb['LoadBalancerArn'].split('/')[-1]),
                        'Type': lb.get('Type', 'N/A'),
                        'Scheme': lb.get('Scheme', 'N/A'),
                        'Region': region,
                        'State': lb.get('State', {}).get('Code', 'N/A'),
                        'VpcId': lb.get('VpcId', 'N/A'),
                    }
                    load_balancers.append(lb_data)
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(load_balancers)} Load Balancers")
        return load_balancers

