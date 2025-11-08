"""AWS Cost Monitoring functionality with resource details"""

import boto3
from datetime import datetime, timedelta
from cloudopti.excel_exporter import ExcelExporter
from cloudopti.recommendations import RecommendationsEngine
from cloudopti.display import DisplayTable
from cloudopti.resource_discovery import ResourceDiscovery
from cloudopti.cloudwatch_metrics import CloudWatchMetrics
from cloudopti.comprehensive_metrics import ComprehensiveMetrics
from cloudopti.instance_analyzer import InstanceAnalyzer
from cloudopti.service_mapper import get_services_to_discover
from cloudopti.cost_mapper import CostMapper
from cloudopti.enhanced_recommendations import EnhancedRecommendations


class AWSCostMonitor:
    """Main class for AWS cost monitoring with resource details"""
    
    def __init__(self):
        """Initialize AWS Cost Monitor"""
        self.ce_client = boto3.client('ce')  # Cost Explorer client
        self.excel_exporter = ExcelExporter()
        self.recommendations_engine = RecommendationsEngine()
        self.display = DisplayTable()
        self.resource_discovery = ResourceDiscovery()
        self.cloudwatch_metrics = CloudWatchMetrics()
        self.comprehensive_metrics = ComprehensiveMetrics()
        self.instance_analyzer = InstanceAnalyzer()
        self.cost_mapper = CostMapper()
        self.enhanced_recommendations = EnhancedRecommendations()
    
    def get_last_month_dates(self):
        """Get start and end dates for last month"""
        today = datetime.now()
        # First day of current month
        first_day_current = today.replace(day=1)
        # Last day of last month
        last_day_last_month = first_day_current - timedelta(days=1)
        # First day of last month
        first_day_last_month = last_day_last_month.replace(day=1)
        
        start_date = first_day_last_month.strftime('%Y-%m-%d')
        end_date = (last_day_last_month + timedelta(days=1)).strftime('%Y-%m-%d')
        
        return start_date, end_date
    
    def fetch_costs_by_service(self):
        """Fetch AWS costs grouped by service"""
        start_date, end_date = self.get_last_month_dates()
        
        print(f"📊 Fetching AWS costs from {start_date} to {end_date}...")
        
        try:
            response = self.ce_client.get_cost_and_usage(
                TimePeriod={
                    'Start': start_date,
                    'End': end_date
                },
                Granularity='MONTHLY',
                Metrics=['UnblendedCost'],
                GroupBy=[
                    {
                        'Type': 'DIMENSION',
                        'Key': 'SERVICE'
                    }
                ]
            )
            
            # Parse the response
            costs_by_service = {}
            total_cost = 0.0
            
            for result in response.get('ResultsByTime', []):
                for group in result.get('Groups', []):
                    service = group['Keys'][0]
                    amount = float(group['Metrics']['UnblendedCost']['Amount'])
                    
                    if amount > 0:
                        costs_by_service[service] = amount
                        total_cost += amount
            
            # Sort by cost (descending)
            costs_by_service = dict(
                sorted(costs_by_service.items(), key=lambda x: x[1], reverse=True)
            )
            
            return costs_by_service, total_cost, start_date, end_date
            
        except Exception as e:
            raise Exception(f"Failed to fetch AWS costs: {str(e)}. "
                          f"Make sure AWS credentials are configured and you have "
                          f"Cost Explorer API permissions (ce:GetCostAndUsage).")
    
    def collect_resource_metrics(self, resources):
        """Collect comprehensive CloudWatch metrics for discovered resources"""
        print("\n" + "="*60)
        print("📈 COLLECTING COMPREHENSIVE RESOURCE METRICS")
        print("="*60)
        
        metrics_data = {}
        
        # Collect EC2 metrics (comprehensive)
        if resources.get('EC2'):
            print("\n📊 Collecting EC2 instance metrics (all available)...")
            for instance in resources['EC2']:
                instance_id = instance['InstanceId']
                region = instance['Region']
                instance_type = instance['InstanceType']
                
                if instance['State'] == 'running':
                    try:
                        print(f"  • {instance_id} ({instance_type})...", end=' ')
                        metrics = self.comprehensive_metrics.get_all_ec2_metrics(instance_id, region, days=7)
                        metrics_data[instance_id] = metrics
                        
                        # Show monitoring status
                        if not metrics.get('monitoring_enabled'):
                            print("⚠ (No monitoring)")
                        elif not metrics.get('cw_agent_installed'):
                            print("✓ (Basic monitoring)")
                        else:
                            print("✓ (Full monitoring)")
                    except Exception as e:
                        print(f"✗ (Error: {str(e)[:50]})")
                        metrics_data[instance_id] = {}
                else:
                    metrics_data[instance_id] = {}
        
        # Collect EKS metrics (comprehensive)
        if resources.get('EKS'):
            print("\n📊 Collecting EKS cluster metrics (all available)...")
            for cluster in resources['EKS']:
                cluster_name = cluster['ClusterName']
                region = cluster['Region']
                
                try:
                    print(f"  • {cluster_name}...", end=' ')
                    metrics = self.comprehensive_metrics.get_all_eks_metrics(cluster_name, region, days=7)
                    metrics_data[cluster_name] = metrics
                    
                    if not metrics.get('container_insights_enabled'):
                        print("⚠ (Container Insights not enabled)")
                    else:
                        print("✓")
                except Exception as e:
                    print(f"✗ (Error: {str(e)[:50]})")
                    metrics_data[cluster_name] = {}
        
        # Collect S3 metrics (comprehensive)
        if resources.get('S3'):
            print("\n📊 Collecting S3 bucket metrics (all available)...")
            for bucket in resources['S3']:
                bucket_name = bucket['BucketName']
                bucket_region = bucket.get('Region', 'us-east-1')
                
                try:
                    print(f"  • {bucket_name}...", end=' ')
                    metrics = self.comprehensive_metrics.get_all_s3_metrics(bucket_name, bucket_region, days=7)
                    metrics_data[bucket_name] = metrics
                    
                    if not metrics.get('monitoring_enabled'):
                        print("⚠ (No metrics)")
                    else:
                        print(f"✓ ({len(metrics.get('available_metrics', []))} metrics)")
                except Exception as e:
                    print(f"✗ (Error: {str(e)[:50]})")
                    metrics_data[bucket_name] = {}
        
        # Collect RDS metrics (comprehensive)
        if resources.get('RDS'):
            print("\n📊 Collecting RDS instance metrics (all available)...")
            for db_instance in resources['RDS']:
                db_id = db_instance['DBInstanceIdentifier']
                region = db_instance['Region']
                
                try:
                    print(f"  • {db_id}...", end=' ')
                    metrics = self.comprehensive_metrics.get_all_rds_metrics(db_id, region, days=7)
                    metrics_data[db_id] = metrics
                    
                    if not metrics.get('monitoring_enabled'):
                        print("⚠ (No monitoring)")
                    else:
                        print(f"✓ ({len(metrics.get('available_metrics', []))} metrics)")
                except Exception as e:
                    print(f"✗ (Error: {str(e)[:50]})")
                    metrics_data[db_id] = {}
        
        return metrics_data
    
    def analyze_resources(self, resources, metrics_data):
        """Analyze resources and generate recommendations"""
        print("\n" + "="*60)
        print("🔬 ANALYZING RESOURCES")
        print("="*60)
        
        analyses = {}
        
        # Analyze EC2 instances
        if resources.get('EC2'):
            print("\n🔍 Analyzing EC2 instances...")
            for instance in resources['EC2']:
                instance_id = instance['InstanceId']
                instance_type = instance['InstanceType']
                region = instance['Region']
                
                metrics = metrics_data.get(instance_id, {})
                
                try:
                    print(f"  • {instance_id} ({instance_type})...", end=' ')
                    analysis = self.instance_analyzer.analyze_instance(
                        instance_id, instance_type, region, metrics
                    )
                    analyses[instance_id] = analysis
                    print("✓")
                except Exception as e:
                    print(f"✗ (Error: {str(e)[:50]})")
                    analyses[instance_id] = {
                        'InstanceId': instance_id,
                        'InstanceType': instance_type,
                        'Region': region,
                        'Recommendation': f"Analysis failed: {str(e)[:100]}"
                    }
        
        return analyses
    
    def run(self):
        """Main execution method"""
        # Fetch costs
        costs_by_service, total_cost, start_date, end_date = self.fetch_costs_by_service()
        
        if not costs_by_service:
            print("✅ No costs found for the last month.")
            return
        
        # Display table
        print("\n" + "="*60)
        print("💰 AWS COST REPORT - LAST MONTH")
        print("="*60)
        self.display.show_table(costs_by_service, total_cost)
        
        # Discover resources based on services in the bill
        services_to_discover = get_services_to_discover(costs_by_service)
        resources = self.resource_discovery.discover_all_resources(services_to_discover)
        
        # Map actual costs to resources
        print("\n" + "="*60)
        print("💰 MAPPING COSTS TO RESOURCES")
        print("="*60)
        resource_costs = self.cost_mapper.map_costs_to_resources(resources, costs_by_service)
        
        # Collect comprehensive metrics
        metrics_data = {}
        analyses = {}
        
        if any(resources.values()):
            metrics_data = self.collect_resource_metrics(resources)
            analyses = self.analyze_resources(resources, metrics_data)
        
        # Generate enhanced recommendations
        print("\n" + "="*60)
        print("💡 DETAILED COST-SAVING RECOMMENDATIONS")
        print("="*60)
        
        # Get basic recommendations
        basic_recommendations = self.recommendations_engine.generate(costs_by_service, total_cost)
        
        # Get enhanced resource-specific recommendations
        resource_recommendations = self.enhanced_recommendations.generate_resource_recommendations(
            resources, metrics_data, resource_costs, analyses
        )
        
        # Get service-level recommendations
        service_recommendations = self.enhanced_recommendations.generate_service_recommendations(
            costs_by_service, total_cost
        )
        
        # Display recommendations
        print("\n📋 Service-Level Recommendations:")
        for rec in basic_recommendations:
            print(f"  • {rec}")
        
        if service_recommendations:
            print("\n🎯 High-Priority Service Recommendations:")
            for rec in service_recommendations[:3]:  # Top 3
                print(f"  • [{rec['severity']}] {rec['title']}")
                print(f"    Reason: {rec['reason']}")
                print(f"    Potential Savings: {rec['potential_savings']}")
        
        if resource_recommendations:
            print(f"\n🔍 Resource-Specific Recommendations ({len(resource_recommendations)} found):")
            high_priority = [r for r in resource_recommendations if r['severity'] == 'HIGH']
            if high_priority:
                print(f"  ⚠ {len(high_priority)} HIGH priority recommendations found!")
                for rec in high_priority[:5]:  # Top 5 high priority
                    print(f"    • {rec['title']}")
                    print(f"      {rec['recommendation']}")
                    print(f"      Savings: {rec['potential_savings']}")
        
        # Combine all recommendations for Excel export
        all_recommendations = basic_recommendations + [
            f"[{r['severity']}] {r['title']}: {r['recommendation']} (Savings: {r['potential_savings']})"
            for r in resource_recommendations + service_recommendations
        ]
        
        # Export to Excel
        filename = self.excel_exporter.export(
            costs_by_service, 
            total_cost, 
            start_date, 
            end_date,
            all_recommendations,
            resources=resources,
            metrics_data=metrics_data,
            analyses=analyses,
            resource_costs=resource_costs
        )
        
        print("\n" + "="*60)
        print(f"✅ Report saved to: {filename}")
        print("="*60)
        print(f"\n📊 Report includes:")
        print(f"  • Summary sheet with cost breakdown")
        if resources.get('EC2'):
            print(f"  • EC2 sheet with {len(resources['EC2'])} instances and optimization recommendations")
        if resources.get('EKS'):
            print(f"  • EKS sheet with {len(resources['EKS'])} clusters")
        if resources.get('S3'):
            print(f"  • S3 sheet with {len(resources['S3'])} buckets")
        if resources.get('VPC'):
            print(f"  • VPC sheet with {len(resources['VPC'])} VPCs")
        print("="*60 + "\n")
