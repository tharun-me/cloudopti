"""Comprehensive CloudWatch Metrics Collection - All available metrics"""

import boto3
from datetime import datetime, timedelta
from botocore.exceptions import ClientError


class ComprehensiveMetrics:
    """Collect all available CloudWatch metrics for resources"""
    
    def __init__(self):
        """Initialize CloudWatch client"""
        session = boto3.Session()
        default_region = session.region_name or 'us-east-1'
        self.default_region = default_region
    
    def list_available_metrics(self, namespace, dimensions, region):
        """List all available metrics for a resource"""
        cw = boto3.client('cloudwatch', region_name=region)
        metrics_list = []
        
        try:
            paginator = cw.get_paginator('list_metrics')
            page_iterator = paginator.paginate(
                Namespace=namespace,
                Dimensions=dimensions
            )
            
            for page in page_iterator:
                for metric in page.get('Metrics', []):
                    metrics_list.append({
                        'MetricName': metric['MetricName'],
                        'Namespace': metric['Namespace'],
                        'Dimensions': metric.get('Dimensions', [])
                    })
        except Exception:
            pass
        
        return metrics_list
    
    def get_all_ec2_metrics(self, instance_id, region, days=7):
        """Get ALL available EC2 metrics"""
        cw = boto3.client('cloudwatch', region_name=region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        dimensions = [{'Name': 'InstanceId', 'Value': instance_id}]
        
        # List all available metrics
        available_metrics = self.list_available_metrics('AWS/EC2', dimensions, region)
        
        metrics = {
            'available_metrics': [m['MetricName'] for m in available_metrics],
            'monitoring_enabled': False,
            'cw_agent_installed': False,
            'detailed_metrics': {}
        }
        
        # Standard EC2 metrics (always available if instance is running)
        standard_metrics = [
            'CPUUtilization', 'NetworkIn', 'NetworkOut', 
            'DiskReadOps', 'DiskWriteOps', 'DiskReadBytes', 'DiskWriteBytes',
            'StatusCheckFailed', 'StatusCheckFailed_Instance', 'StatusCheckFailed_System'
        ]
        
        # Enhanced metrics (require CloudWatch agent)
        enhanced_metrics = [
            'mem_used_percent', 'mem_available', 'mem_used',
            'disk_used_percent', 'disk_used', 'disk_total',
            'procstat_cpu_usage', 'procstat_memory_usage'
        ]
        
        # Check if enhanced metrics are available (indicates CW agent)
        has_enhanced = any(m['MetricName'] in enhanced_metrics for m in available_metrics)
        metrics['cw_agent_installed'] = has_enhanced
        
        # Collect standard metrics
        for metric_name in standard_metrics:
            try:
                data = cw.get_metric_statistics(
                    Namespace='AWS/EC2',
                    MetricName=metric_name,
                    Dimensions=dimensions,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,
                    Statistics=['Average', 'Maximum', 'Minimum', 'Sum']
                )
                
                if data:
                    metrics['monitoring_enabled'] = True
                    if metric_name == 'CPUUtilization':
                        metrics['detailed_metrics'][metric_name] = {
                            'avg': sum(d.get('Average', 0) for d in data) / len(data) if data else 0,
                            'max': max(d.get('Maximum', 0) for d in data) if data else 0,
                            'min': min(d.get('Minimum', 0) for d in data) if data else 0,
                            'datapoints': len(data)
                        }
                    elif metric_name in ['NetworkIn', 'NetworkOut', 'DiskReadBytes', 'DiskWriteBytes']:
                        metrics['detailed_metrics'][metric_name] = {
                            'total': sum(d.get('Sum', 0) for d in data) if data else 0,
                            'avg': sum(d.get('Average', 0) for d in data) / len(data) if data else 0,
                            'datapoints': len(data)
                        }
                    else:
                        metrics['detailed_metrics'][metric_name] = {
                            'avg': sum(d['Average'] for d in data) / len(data) if data else 0,
                            'datapoints': len(data)
                        }
            except Exception:
                pass
        
        # Collect enhanced metrics if available
        if has_enhanced:
            for metric_name in enhanced_metrics:
                try:
                    data = cw.get_metric_statistics(
                        Namespace='CWAgent',
                        MetricName=metric_name,
                        Dimensions=dimensions,
                        StartTime=start_time,
                        EndTime=end_time,
                        Period=3600,
                        Statistics=['Average', 'Maximum']
                    )
                    
                    if data:
                        metrics['detailed_metrics'][metric_name] = {
                            'avg': sum(d['Average'] for d in data) / len(data) if data else 0,
                            'max': max(d['Maximum'] for d in data) if data else 0,
                            'datapoints': len(data)
                        }
                except Exception:
                    pass
        
        return metrics
    
    def get_all_rds_metrics(self, db_instance_id, region, days=7):
        """Get ALL available RDS metrics"""
        cw = boto3.client('cloudwatch', region_name=region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        dimensions = [{'Name': 'DBInstanceIdentifier', 'Value': db_instance_id}]
        
        # Standard RDS metrics
        rds_metrics = [
            'CPUUtilization', 'DatabaseConnections', 'FreeableMemory',
            'FreeStorageSpace', 'ReadLatency', 'WriteLatency',
            'ReadIOPS', 'WriteIOPS', 'ReadThroughput', 'WriteThroughput',
            'NetworkReceiveThroughput', 'NetworkTransmitThroughput',
            'DiskQueueDepth', 'SwapUsage', 'BinLogDiskUsage'
        ]
        
        metrics = {
            'available_metrics': [],
            'monitoring_enabled': False,
            'detailed_metrics': {}
        }
        
        for metric_name in rds_metrics:
            try:
                data = cw.get_metric_statistics(
                    Namespace='AWS/RDS',
                    MetricName=metric_name,
                    Dimensions=dimensions,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,
                    Statistics=['Average', 'Maximum']
                )
                
                if data:
                    metrics['monitoring_enabled'] = True
                    metrics['available_metrics'].append(metric_name)
                    metrics['detailed_metrics'][metric_name] = {
                        'avg': sum(d['Average'] for d in data) / len(data) if data else 0,
                        'max': max(d['Maximum'] for d in data) if data else 0,
                        'datapoints': len(data)
                    }
            except Exception:
                pass
        
        return metrics
    
    def get_all_eks_metrics(self, cluster_name, region, days=7):
        """Get ALL available EKS metrics"""
        cw = boto3.client('cloudwatch', region_name=region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        # Try ContainerInsights namespace first
        dimensions = [{'Name': 'ClusterName', 'Value': cluster_name}]
        
        metrics = {
            'available_metrics': [],
            'monitoring_enabled': False,
            'container_insights_enabled': False,
            'detailed_metrics': {}
        }
        
        # Container Insights metrics
        container_metrics = [
            'node_cpu_utilization', 'node_memory_utilization',
            'node_network_total_bytes', 'pod_cpu_utilization',
            'pod_memory_utilization', 'pod_network_rx_bytes',
            'pod_network_tx_bytes', 'cluster_failed_node_count'
        ]
        
        for metric_name in container_metrics:
            try:
                data = cw.get_metric_statistics(
                    Namespace='ContainerInsights',
                    MetricName=metric_name,
                    Dimensions=dimensions,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=3600,
                    Statistics=['Average', 'Maximum']
                )
                
                if data:
                    metrics['container_insights_enabled'] = True
                    metrics['monitoring_enabled'] = True
                    metrics['available_metrics'].append(metric_name)
                    metrics['detailed_metrics'][metric_name] = {
                        'avg': sum(d['Average'] for d in data) / len(data) if data else 0,
                        'max': max(d['Maximum'] for d in data) if data else 0,
                        'datapoints': len(data)
                    }
            except Exception:
                pass
        
        return metrics
    
    def get_all_s3_metrics(self, bucket_name, region, days=7):
        """Get ALL available S3 metrics"""
        cw = boto3.client('cloudwatch', region_name=region)
        
        end_time = datetime.utcnow()
        start_time = end_time - timedelta(days=days)
        
        dimensions = [{'Name': 'BucketName', 'Value': bucket_name}]
        
        metrics = {
            'available_metrics': [],
            'monitoring_enabled': False,
            'detailed_metrics': {}
        }
        
        s3_metrics = [
            'BucketSizeBytes', 'NumberOfObjects', 'AllRequests',
            'GetRequests', 'PutRequests', 'DeleteRequests',
            'HeadRequests', 'PostRequests', 'ListRequests',
            'BytesDownloaded', 'BytesUploaded', '4xxErrors', '5xxErrors'
        ]
        
        for metric_name in s3_metrics:
            try:
                data = cw.get_metric_statistics(
                    Namespace='AWS/S3',
                    MetricName=metric_name,
                    Dimensions=dimensions,
                    StartTime=start_time,
                    EndTime=end_time,
                    Period=86400,  # Daily for S3
                    Statistics=['Average', 'Sum']
                )
                
                if data:
                    metrics['monitoring_enabled'] = True
                    metrics['available_metrics'].append(metric_name)
                    if metric_name in ['BucketSizeBytes', 'NumberOfObjects']:
                        metrics['detailed_metrics'][metric_name] = {
                            'avg': sum(d['Average'] for d in data) / len(data) if data else 0,
                            'datapoints': len(data)
                        }
                    else:
                        metrics['detailed_metrics'][metric_name] = {
                            'total': sum(d['Sum'] for d in data) if data else 0,
                            'datapoints': len(data)
                        }
            except Exception:
                pass
        
        return metrics

