"""CloudWatch Metrics Collection - CPU, Memory, Disk usage"""

import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


class CloudWatchMetrics:
    """Collect CloudWatch metrics for resources"""
    
    def __init__(self):
        """Initialize CloudWatch client"""
        # Get default region from AWS config or use us-east-1 as fallback
        session = boto3.Session()
        default_region = session.region_name or 'us-east-1'
        self.cw_client = boto3.client('cloudwatch', region_name=default_region)
    
    def get_metric_statistics(self, namespace, metric_name, dimensions, 
                             start_time, end_time, period=3600, statistic='Average'):
        """Get CloudWatch metric statistics"""
        try:
            response = self.cw_client.get_metric_statistics(
                Namespace=namespace,
                MetricName=metric_name,
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=period,
                Statistics=[statistic]
            )
            return response.get('Datapoints', [])
        except ClientError:
            return []
        except Exception:
            return []
    
    def get_ec2_metrics(self, instance_id, region, days=7):
        """Get EC2 instance metrics (CPU, Network, Disk)"""
        cw = boto3.client('cloudwatch', region_name=region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        dimensions = [{'Name': 'InstanceId', 'Value': instance_id}]
        
        metrics = {
            'CPUUtilization': [],
            'NetworkIn': [],
            'NetworkOut': [],
            'DiskReadOps': [],
            'DiskWriteOps': [],
        }
        
        # CPU Utilization
        try:
            cpu_data = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='CPUUtilization',
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average', 'Maximum']
            )
            if cpu_data:
                metrics['CPUUtilization'] = {
                    'avg': sum(d['Average'] for d in cpu_data) / len(cpu_data) if cpu_data else 0,
                    'max': max(d['Maximum'] for d in cpu_data) if cpu_data else 0,
                    'datapoints': len(cpu_data)
                }
        except Exception:
            pass
        
        # Network In
        try:
            net_in = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkIn',
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            if net_in:
                metrics['NetworkIn'] = {
                    'total': sum(d['Sum'] for d in net_in),
                    'datapoints': len(net_in)
                }
        except Exception:
            pass
        
        # Network Out
        try:
            net_out = cw.get_metric_statistics(
                Namespace='AWS/EC2',
                MetricName='NetworkOut',
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Sum']
            )
            if net_out:
                metrics['NetworkOut'] = {
                    'total': sum(d['Sum'] for d in net_out),
                    'datapoints': len(net_out)
                }
        except Exception:
            pass
        
        return metrics
    
    def get_eks_metrics(self, cluster_name, region, days=7):
        """Get EKS cluster metrics"""
        cw = boto3.client('cloudwatch', region_name=region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        dimensions = [{'Name': 'ClusterName', 'Value': cluster_name}]
        
        metrics = {}
        
        # CPU Utilization
        try:
            cpu_data = cw.get_metric_statistics(
                Namespace='ContainerInsights',
                MetricName='node_cpu_utilization',
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average']
            )
            if cpu_data:
                metrics['CPUUtilization'] = {
                    'avg': sum(d['Average'] for d in cpu_data) / len(cpu_data) if cpu_data else 0,
                    'datapoints': len(cpu_data)
                }
        except Exception:
            pass
        
        # Memory Utilization
        try:
            mem_data = cw.get_metric_statistics(
                Namespace='ContainerInsights',
                MetricName='node_memory_utilization',
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=3600,
                Statistics=['Average']
            )
            if mem_data:
                metrics['MemoryUtilization'] = {
                    'avg': sum(d['Average'] for d in mem_data) / len(mem_data) if mem_data else 0,
                    'datapoints': len(mem_data)
                }
        except Exception:
            pass
        
        return metrics
    
    def get_s3_metrics(self, bucket_name, region='us-east-1', days=7):
        """Get S3 bucket metrics"""
        # CloudWatch metrics for S3 are region-specific
        cw = boto3.client('cloudwatch', region_name=region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        dimensions = [{'Name': 'BucketName', 'Value': bucket_name}]
        
        metrics = {}
        
        # Bucket Size
        try:
            size_data = cw.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='BucketSizeBytes',
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,  # Daily
                Statistics=['Average']
            )
            if size_data:
                metrics['BucketSize'] = {
                    'avg': sum(d['Average'] for d in size_data) / len(size_data) if size_data else 0,
                    'datapoints': len(size_data)
                }
        except Exception:
            pass
        
        # Number of Objects
        try:
            obj_data = cw.get_metric_statistics(
                Namespace='AWS/S3',
                MetricName='NumberOfObjects',
                Dimensions=dimensions,
                StartTime=start_time,
                EndTime=end_time,
                Period=86400,
                Statistics=['Average']
            )
            if obj_data:
                metrics['NumberOfObjects'] = {
                    'avg': sum(d['Average'] for d in obj_data) / len(obj_data) if obj_data else 0,
                    'datapoints': len(obj_data)
                }
        except Exception:
            pass
        
        return metrics

