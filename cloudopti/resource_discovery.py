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
    
    def discover_all_resources(self, services_to_discover=None, service_mapping=None):
        """Discover all resources based on services in the bill"""
        print("\n" + "="*60)
        print("🔍 RESOURCE DISCOVERY (Based on Bill)")
        print("="*60)
        
        # If no services specified, don't discover anything
        if services_to_discover is None or len(services_to_discover) == 0:
            print("⚠️  No services found in bill to discover resources for.")
            return {}
        
        # Show which services from the bill will be discovered (in bill order)
        if service_mapping:
            print("\n📋 Services in bill that will be analyzed (ordered by cost):")
            for discovery_key in services_to_discover:
                bill_services = service_mapping.get(discovery_key, [])
                # Sort bill services by cost (highest first)
                bill_services_sorted = sorted(bill_services, key=lambda x: x['cost'], reverse=True)
                for bill_service in bill_services_sorted:
                    print(f"  • {bill_service['bill_name']} (${bill_service['cost']:.2f}) → {discovery_key}")
        
        print(f"\n🔍 Discovering resources for: {', '.join(services_to_discover)} (in bill order)")
        
        resources = {}
        
        # Discover resources in the order they appear in the bill (by cost, highest first)
        # This ensures discovery happens in bill order
        for discovery_key in services_to_discover:
            if discovery_key == 'EC2':
                resources['EC2'] = self.discover_ec2_instances()
            elif discovery_key == 'EKS':
                resources['EKS'] = self.discover_eks_clusters()
            elif discovery_key == 'RDS':
                resources['RDS'] = self.discover_rds_instances()
            elif discovery_key == 'VPC':
                resources['VPC'] = self.discover_vpcs()
            elif discovery_key == 'S3':
                resources['S3'] = self.discover_s3_buckets()
            elif discovery_key == 'Lambda':
                resources['Lambda'] = self.discover_lambda_functions()
            elif discovery_key == 'DynamoDB':
                resources['DynamoDB'] = self.discover_dynamodb_tables()
            elif discovery_key == 'ELB':
                resources['ELB'] = self.discover_load_balancers()
            elif discovery_key == 'Route53':
                resources['Route53'] = self.discover_route53_hosted_zones()
            elif discovery_key == 'SecretsManager':
                resources['SecretsManager'] = self.discover_secrets_manager_secrets()
            elif discovery_key == 'SystemsManager':
                resources['SystemsManager'] = self.discover_systems_manager_instances()
            elif discovery_key == 'CloudWatch':
                resources['CloudWatch'] = self.discover_cloudwatch_alarms()
            elif discovery_key == 'GuardDuty':
                resources['GuardDuty'] = self.discover_guardduty_detectors()
        
        # Show summary
        total_resources = sum(len(v) for v in resources.values())
        print(f"\n✅ Discovery complete: Found {total_resources} total resources across {len(resources)} services")
        
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
    
    def discover_route53_hosted_zones(self):
        """Discover all Route53 hosted zones"""
        print("🔍 Discovering Route53 hosted zones...")
        hosted_zones = []
        
        try:
            route53 = boto3.client('route53')
            response = route53.list_hosted_zones()
            
            for zone in response.get('HostedZones', []):
                zone_data = {
                    'HostedZoneId': zone['Id'].split('/')[-1],
                    'Name': zone['Name'],
                    'PrivateZone': zone.get('Config', {}).get('PrivateZone', False),
                    'ResourceRecordSetCount': zone.get('ResourceRecordSetCount', 0),
                }
                hosted_zones.append(zone_data)
        except ClientError:
            pass
        except Exception:
            pass
        
        print(f"  ✓ Found {len(hosted_zones)} Route53 hosted zones")
        return hosted_zones
    
    def discover_secrets_manager_secrets(self):
        """Discover all Secrets Manager secrets across regions"""
        print("🔍 Discovering Secrets Manager secrets...")
        secrets = []
        
        for region in self.regions:
            try:
                sm = boto3.client('secretsmanager', region_name=region)
                response = sm.list_secrets()
                
                for secret in response.get('SecretList', []):
                    secret_data = {
                        'SecretName': secret.get('Name', 'N/A'),
                        'ARN': secret.get('ARN', 'N/A'),
                        'Region': region,
                        'Description': secret.get('Description', 'N/A'),
                        'LastChangedDate': secret.get('LastChangedDate', datetime.now()),
                        'LastAccessedDate': secret.get('LastAccessedDate', datetime.now()),
                    }
                    secrets.append(secret_data)
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(secrets)} Secrets Manager secrets")
        return secrets
    
    def discover_systems_manager_instances(self):
        """Discover all Systems Manager managed instances"""
        print("🔍 Discovering Systems Manager instances...")
        instances = []
        
        for region in self.regions:
            try:
                ssm = boto3.client('ssm', region_name=region)
                response = ssm.describe_instance_information()
                
                for instance_info in response.get('InstanceInformationList', []):
                    instance_data = {
                        'InstanceId': instance_info.get('InstanceId', 'N/A'),
                        'ComputerName': instance_info.get('ComputerName', 'N/A'),
                        'PlatformType': instance_info.get('PlatformType', 'N/A'),
                        'PlatformVersion': instance_info.get('PlatformVersion', 'N/A'),
                        'Region': region,
                        'PingStatus': instance_info.get('PingStatus', 'N/A'),
                        'LastPingDateTime': instance_info.get('LastPingDateTime', datetime.now()),
                    }
                    instances.append(instance_data)
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(instances)} Systems Manager instances")
        return instances
    
    def discover_cloudwatch_alarms(self):
        """Discover all CloudWatch alarms across regions"""
        print("🔍 Discovering CloudWatch alarms...")
        alarms = []
        
        for region in self.regions:
            try:
                cw = boto3.client('cloudwatch', region_name=region)
                response = cw.describe_alarms()
                
                for alarm in response.get('MetricAlarms', []):
                    alarm_data = {
                        'AlarmName': alarm.get('AlarmName', 'N/A'),
                        'Namespace': alarm.get('Namespace', 'N/A'),
                        'MetricName': alarm.get('MetricName', 'N/A'),
                        'StateValue': alarm.get('StateValue', 'N/A'),
                        'StateUpdatedTimestamp': alarm.get('StateUpdatedTimestamp', datetime.now()),
                        'Region': region,
                    }
                    alarms.append(alarm_data)
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(alarms)} CloudWatch alarms")
        return alarms
    
    def discover_guardduty_detectors(self):
        """Discover all GuardDuty detectors across regions"""
        print("🔍 Discovering GuardDuty detectors...")
        detectors = []
        
        for region in self.regions:
            try:
                gd = boto3.client('guardduty', region_name=region)
                response = gd.list_detectors()
                
                for detector_id in response.get('DetectorIds', []):
                    try:
                        detector_detail = gd.get_detector(DetectorId=detector_id)
                        detector_data = {
                            'DetectorId': detector_id,
                            'Region': region,
                            'Status': detector_detail.get('Status', 'N/A'),
                            'CreatedAt': detector_detail.get('CreatedAt', datetime.now()),
                            'FindingPublishingFrequency': detector_detail.get('FindingPublishingFrequency', 'N/A'),
                        }
                        detectors.append(detector_data)
                    except Exception:
                        continue
            except ClientError:
                continue
            except Exception:
                continue
        
        print(f"  ✓ Found {len(detectors)} GuardDuty detectors")
        return detectors

