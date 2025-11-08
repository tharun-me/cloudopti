"""Enhanced Recommendations Engine with detailed reasoning"""


class EnhancedRecommendations:
    """Generate detailed cost-saving recommendations with reasoning"""
    
    def __init__(self):
        """Initialize recommendations engine"""
        pass
    
    def generate_resource_recommendations(self, resources, metrics_data, resource_costs, analyses):
        """Generate detailed recommendations for each resource"""
        recommendations = []
        
        # EC2 recommendations
        if resources.get('EC2') and analyses:
            for instance in resources['EC2']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                state = instance['State']
                region = instance['Region']
                
                analysis = analyses.get(instance_id, {})
                metrics = metrics_data.get(instance_id, {})
                cost = resource_costs.get('EC2', {}).get(instance_id, 0)
                
                # Check monitoring status
                if not metrics.get('monitoring_enabled', False):
                    recommendations.append({
                        'resource_id': instance_id,
                        'resource_type': 'EC2',
                        'severity': 'HIGH',
                        'title': f'EC2 Instance {instance_id} - CloudWatch Monitoring Not Enabled',
                        'description': f'Instance {instance_id} ({instance_type}) in {region} does not have CloudWatch monitoring enabled.',
                        'reason': 'Without CloudWatch monitoring, you cannot track CPU, memory, disk, and network usage. This makes it impossible to optimize instance sizing and identify performance issues.',
                        'recommendation': 'Enable CloudWatch monitoring for this instance. For detailed metrics (memory, disk), install the CloudWatch agent.',
                        'action': 'Enable detailed monitoring: aws ec2 monitor-instances --instance-ids ' + instance_id,
                        'potential_savings': 'Unknown (cannot optimize without metrics)',
                        'cost_impact': f'Current cost: ${cost:.2f}/month'
                    })
                
                # Check CloudWatch agent
                if not metrics.get('cw_agent_installed', False) and state == 'running':
                    recommendations.append({
                        'resource_id': instance_id,
                        'resource_type': 'EC2',
                        'severity': 'MEDIUM',
                        'title': f'EC2 Instance {instance_id} - CloudWatch Agent Not Installed',
                        'description': f'Instance {instance_id} ({instance_type}) is missing the CloudWatch agent.',
                        'reason': 'The CloudWatch agent provides detailed metrics including memory utilization, disk usage, and process-level metrics. Without it, you only get basic CPU and network metrics.',
                        'recommendation': 'Install the CloudWatch agent to get comprehensive metrics. This will enable better right-sizing recommendations.',
                        'action': 'Install CloudWatch agent: https://docs.aws.amazon.com/AmazonCloudWatch/latest/monitoring/Install-CloudWatch-Agent.html',
                        'potential_savings': 'Enables accurate optimization recommendations',
                        'cost_impact': f'Current cost: ${cost:.2f}/month'
                    })
                
                # Right-sizing recommendations
                if analysis.get('RecommendedType') and analysis.get('RecommendedType') != instance_type:
                    savings = analysis.get('PotentialSavings', 0)
                    savings_percent = analysis.get('SavingsPercent', 0)
                    cpu_avg = analysis.get('CPUUsageAvg', 0)
                    cpu_max = analysis.get('CPUUsageMax', 0)
                    
                    if savings > 0:
                        recommendations.append({
                            'resource_id': instance_id,
                            'resource_type': 'EC2',
                            'severity': 'HIGH',
                            'title': f'EC2 Instance {instance_id} - Right-Sizing Opportunity',
                            'description': f'Instance {instance_id} is over-provisioned. Current type: {instance_type}, Recommended: {analysis["RecommendedType"]}',
                            'reason': f'Current CPU usage: Average {cpu_avg:.1f}%, Maximum {cpu_max:.1f}%. The instance is significantly underutilized, indicating it can be downsized.',
                            'recommendation': f'Downsize to {analysis["RecommendedType"]} to reduce costs while maintaining performance.',
                            'action': f'Stop instance, change instance type to {analysis["RecommendedType"]}, and restart.',
                            'potential_savings': f'${savings:.2f}/month ({savings_percent:.1f}% reduction)',
                            'cost_impact': f'Current: ${cost:.2f}/month → Potential: ${cost - savings:.2f}/month'
                        })
                    elif savings < 0:
                        recommendations.append({
                            'resource_id': instance_id,
                            'resource_type': 'EC2',
                            'severity': 'MEDIUM',
                            'title': f'EC2 Instance {instance_id} - Performance Risk',
                            'description': f'Instance {instance_id} may be under-provisioned. Current type: {instance_type}, Recommended: {analysis["RecommendedType"]}',
                            'reason': f'High CPU usage detected: Average {cpu_avg:.1f}%, Maximum {cpu_max:.1f}%. The instance is approaching capacity limits.',
                            'recommendation': f'Consider upgrading to {analysis["RecommendedType"]} to prevent performance degradation.',
                            'action': f'Monitor closely and upgrade if performance issues occur.',
                            'potential_savings': 'N/A (performance improvement)',
                            'cost_impact': f'Current: ${cost:.2f}/month → Upgrade: ${cost - savings:.2f}/month'
                        })
                
                # Stopped instances
                if state == 'stopped' and cost > 0:
                    recommendations.append({
                        'resource_id': instance_id,
                        'resource_type': 'EC2',
                        'severity': 'HIGH',
                        'title': f'EC2 Instance {instance_id} - Stopped but Incurring Costs',
                        'description': f'Instance {instance_id} is stopped but still showing costs.',
                        'reason': 'Stopped instances should not incur compute costs. If costs are appearing, check for EBS volumes, Elastic IPs, or other attached resources.',
                        'recommendation': 'Review attached resources (EBS volumes, Elastic IPs) and terminate if not needed.',
                        'action': 'Check EBS volumes: aws ec2 describe-volumes --filters Name=attachment.instance-id,Values=' + instance_id,
                        'potential_savings': f'${cost:.2f}/month',
                        'cost_impact': f'Current cost: ${cost:.2f}/month'
                    })
        
        # RDS recommendations
        if resources.get('RDS'):
            for db_instance in resources['RDS']:
                db_id = db_instance['DBInstanceIdentifier']
                db_class = db_instance['DBInstanceClass']
                status = db_instance['Status']
                multi_az = db_instance['MultiAZ']
                cost = resource_costs.get('RDS', {}).get(db_id, 0)
                
                # Multi-AZ for non-production
                if multi_az and status != 'available':
                    recommendations.append({
                        'resource_id': db_id,
                        'resource_type': 'RDS',
                        'severity': 'MEDIUM',
                        'title': f'RDS Instance {db_id} - Multi-AZ for Non-Production',
                        'description': f'RDS instance {db_id} has Multi-AZ enabled but is not in production status.',
                        'reason': 'Multi-AZ doubles your RDS costs. For development/test environments, Single-AZ is sufficient and can save 50% on database costs.',
                        'recommendation': 'Disable Multi-AZ for non-production databases to reduce costs.',
                        'action': f'Modify RDS instance {db_id} and disable Multi-AZ.',
                        'potential_savings': f'${cost * 0.5:.2f}/month (50% reduction)',
                        'cost_impact': f'Current: ${cost:.2f}/month → Potential: ${cost * 0.5:.2f}/month'
                    })
        
        # S3 recommendations
        if resources.get('S3'):
            for bucket in resources['S3']:
                bucket_name = bucket['BucketName']
                size_gb = bucket.get('Size', 0) / (1024**3)
                storage_classes = bucket.get('StorageClass', {})
                cost = resource_costs.get('S3', {}).get(bucket_name, 0)
                
                # Check for Standard storage only
                if 'STANDARD' in storage_classes and len(storage_classes) == 1 and size_gb > 100:
                    standard_size = storage_classes['STANDARD'] / (1024**3)
                    recommendations.append({
                        'resource_id': bucket_name,
                        'resource_type': 'S3',
                        'severity': 'MEDIUM',
                        'title': f'S3 Bucket {bucket_name} - All Data in Standard Storage',
                        'description': f'Bucket {bucket_name} has {standard_size:.2f} GB in Standard storage class.',
                        'reason': 'S3 Standard is the most expensive storage class. For infrequently accessed data, S3 Intelligent-Tiering or S3 Glacier can reduce costs by 40-68%.',
                        'recommendation': 'Enable S3 Intelligent-Tiering or lifecycle policies to automatically move old data to cheaper storage classes.',
                        'action': f'Create lifecycle policy for bucket {bucket_name} to transition objects older than 30 days to Intelligent-Tiering.',
                        'potential_savings': f'${cost * 0.4:.2f}/month (40% reduction for infrequent access)',
                        'cost_impact': f'Current: ${cost:.2f}/month → Potential: ${cost * 0.4:.2f}/month'
                    })
        
        return recommendations
    
    def generate_service_recommendations(self, costs_by_service, total_cost):
        """Generate high-level service recommendations"""
        recommendations = []
        
        sorted_services = sorted(costs_by_service.items(), key=lambda x: x[1], reverse=True)
        
        # Top cost service analysis
        if sorted_services:
            top_service, top_cost = sorted_services[0]
            if top_cost > 100:
                recommendations.append({
                    'type': 'SERVICE',
                    'severity': 'HIGH',
                    'title': f'{top_service} - Highest Cost Service',
                    'description': f'{top_service} accounts for ${top_cost:.2f} ({top_cost/total_cost*100:.1f}%) of total costs.',
                    'reason': f'This service is your largest cost driver. Focus optimization efforts here for maximum impact.',
                    'recommendation': 'Review all resources in this service. Look for unused resources, right-sizing opportunities, and Reserved Instance options.',
                    'potential_savings': f'Up to ${top_cost * 0.3:.2f}/month (30% potential savings)',
                    'cost_impact': f'Current: ${top_cost:.2f}/month'
                })
        
        # EKS cost analysis
        if 'Amazon Elastic Container Service for Kubernetes' in costs_by_service:
            eks_cost = costs_by_service['Amazon Elastic Container Service for Kubernetes']
            if eks_cost > 200:
                recommendations.append({
                    'type': 'SERVICE',
                    'severity': 'HIGH',
                    'title': 'EKS - High Container Service Costs',
                    'description': f'EKS costs ${eks_cost:.2f}/month. This includes control plane ($0.10/hour) and node costs.',
                    'reason': 'EKS control plane costs $73/month regardless of usage. Consider Fargate for serverless workloads or optimize node groups.',
                    'recommendation': 'Review node group sizes, use Spot Instances for non-critical workloads, and consider Fargate for variable workloads.',
                    'potential_savings': f'${eks_cost * 0.2:.2f}/month (20% potential savings)',
                    'cost_impact': f'Current: ${eks_cost:.2f}/month'
                })
        
        # RDS Reserved Instances
        if 'Amazon Relational Database Service' in costs_by_service:
            rds_cost = costs_by_service['Amazon Relational Database Service']
            if rds_cost > 100:
                recommendations.append({
                    'type': 'SERVICE',
                    'severity': 'MEDIUM',
                    'title': 'RDS - Reserved Instance Opportunity',
                    'description': f'RDS costs ${rds_cost:.2f}/month. Reserved Instances can save up to 75% for steady workloads.',
                    'reason': 'If your RDS instances run 24/7, Reserved Instances provide significant savings compared to On-Demand pricing.',
                    'recommendation': 'Purchase Reserved Instances for production databases that run continuously. 1-year term saves ~40%, 3-year saves ~60%.',
                    'potential_savings': f'${rds_cost * 0.4:.2f}/month (40% with 1-year RI)',
                    'cost_impact': f'Current: ${rds_cost:.2f}/month → Potential: ${rds_cost * 0.6:.2f}/month'
                })
        
        return recommendations

