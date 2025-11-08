"""Instance Type Analyzer - Analyze instance specs and recommend optimizations"""

# EC2 Instance Type Specifications (vCPU, Memory in GiB, Network Performance)
# This is a subset - you can expand this with more instance types
INSTANCE_SPECS = {
    't2.micro': {'vCPU': 1, 'Memory': 1, 'Network': 'Low', 'PricePerHour': 0.0116},
    't2.small': {'vCPU': 1, 'Memory': 2, 'Network': 'Low', 'PricePerHour': 0.023},
    't2.medium': {'vCPU': 2, 'Memory': 4, 'Network': 'Low', 'PricePerHour': 0.0464},
    't2.large': {'vCPU': 2, 'Memory': 8, 'Network': 'Low', 'PricePerHour': 0.0928},
    't2.xlarge': {'vCPU': 4, 'Memory': 16, 'Network': 'Moderate', 'PricePerHour': 0.1856},
    't2.2xlarge': {'vCPU': 8, 'Memory': 32, 'Network': 'Moderate', 'PricePerHour': 0.3712},
    
    't3.micro': {'vCPU': 2, 'Memory': 1, 'Network': 'Low', 'PricePerHour': 0.0104},
    't3.small': {'vCPU': 2, 'Memory': 2, 'Network': 'Low', 'PricePerHour': 0.0208},
    't3.medium': {'vCPU': 2, 'Memory': 4, 'Network': 'Low', 'PricePerHour': 0.0416},
    't3.large': {'vCPU': 2, 'Memory': 8, 'Network': 'Low', 'PricePerHour': 0.0832},
    't3.xlarge': {'vCPU': 4, 'Memory': 16, 'Network': 'Up to 5', 'PricePerHour': 0.1664},
    't3.2xlarge': {'vCPU': 8, 'Memory': 32, 'Network': 'Up to 5', 'PricePerHour': 0.3328},
    
    'm5.large': {'vCPU': 2, 'Memory': 8, 'Network': 'Up to 10', 'PricePerHour': 0.096},
    'm5.xlarge': {'vCPU': 4, 'Memory': 16, 'Network': 'Up to 10', 'PricePerHour': 0.192},
    'm5.2xlarge': {'vCPU': 8, 'Memory': 32, 'Network': 'Up to 10', 'PricePerHour': 0.384},
    'm5.4xlarge': {'vCPU': 16, 'Memory': 64, 'Network': 'Up to 10', 'PricePerHour': 0.768},
    
    'm5a.large': {'vCPU': 2, 'Memory': 8, 'Network': 'Up to 10', 'PricePerHour': 0.0864},
    'm5a.xlarge': {'vCPU': 4, 'Memory': 16, 'Network': 'Up to 10', 'PricePerHour': 0.1728},
    'm5a.2xlarge': {'vCPU': 8, 'Memory': 32, 'Network': 'Up to 10', 'PricePerHour': 0.3456},
    
    'c5.large': {'vCPU': 2, 'Memory': 4, 'Network': 'Up to 10', 'PricePerHour': 0.085},
    'c5.xlarge': {'vCPU': 4, 'Memory': 8, 'Network': 'Up to 10', 'PricePerHour': 0.17},
    'c5.2xlarge': {'vCPU': 8, 'Memory': 16, 'Network': 'Up to 10', 'PricePerHour': 0.34},
    'c5.4xlarge': {'vCPU': 16, 'Memory': 32, 'Network': 'Up to 10', 'PricePerHour': 0.68},
    
    'r5.large': {'vCPU': 2, 'Memory': 16, 'Network': 'Up to 10', 'PricePerHour': 0.126},
    'r5.xlarge': {'vCPU': 4, 'Memory': 32, 'Network': 'Up to 10', 'PricePerHour': 0.252},
    'r5.2xlarge': {'vCPU': 8, 'Memory': 64, 'Network': 'Up to 10', 'PricePerHour': 0.504},
    'r5.4xlarge': {'vCPU': 16, 'Memory': 128, 'Network': 'Up to 10', 'PricePerHour': 1.008},
    
    'i3.large': {'vCPU': 2, 'Memory': 15.25, 'Network': 'Up to 10', 'PricePerHour': 0.156},
    'i3.xlarge': {'vCPU': 4, 'Memory': 30.5, 'Network': 'Up to 10', 'PricePerHour': 0.312},
    'i3.2xlarge': {'vCPU': 8, 'Memory': 61, 'Network': 'Up to 10', 'PricePerHour': 0.624},
}


class InstanceAnalyzer:
    """Analyze instance types and provide optimization recommendations"""
    
    def __init__(self):
        """Initialize analyzer"""
        self.instance_specs = INSTANCE_SPECS
    
    def get_instance_specs(self, instance_type):
        """Get specifications for an instance type"""
        return self.instance_specs.get(instance_type, {
            'vCPU': 'N/A',
            'Memory': 'N/A',
            'Network': 'N/A',
            'PricePerHour': 0
        })
    
    def calculate_monthly_cost(self, instance_type, hours=730):
        """Calculate monthly cost (730 hours = ~1 month)"""
        specs = self.get_instance_specs(instance_type)
        return specs.get('PricePerHour', 0) * hours
    
    def recommend_instance_type(self, current_type, cpu_usage_avg, cpu_usage_max, 
                                memory_usage_avg=None, memory_usage_max=None):
        """Recommend optimal instance type based on usage"""
        current_specs = self.get_instance_specs(current_type)
        
        if current_specs['vCPU'] == 'N/A':
            return None, 0, 0
        
        current_vcpu = current_specs['vCPU']
        current_memory = current_specs['Memory']
        current_cost = self.calculate_monthly_cost(current_type)
        
        # Calculate required resources based on max usage with 20% buffer
        required_vcpu = max(1, int((cpu_usage_max / 100) * current_vcpu * 1.2))
        required_memory = current_memory
        if memory_usage_max:
            required_memory = max(1, int((memory_usage_max / 100) * current_memory * 1.2))
        
        # Find suitable instance types
        recommendations = []
        
        for inst_type, specs in self.instance_specs.items():
            if specs['vCPU'] == 'N/A':
                continue
            
            # Check if instance meets requirements
            if specs['vCPU'] >= required_vcpu and specs['Memory'] >= required_memory:
                inst_cost = self.calculate_monthly_cost(inst_type)
                savings = current_cost - inst_cost
                savings_percent = (savings / current_cost * 100) if current_cost > 0 else 0
                
                # Prefer instances that are not over-provisioned
                vcpu_utilization = (required_vcpu / specs['vCPU']) * 100
                memory_utilization = (required_memory / specs['Memory']) * 100
                
                recommendations.append({
                    'InstanceType': inst_type,
                    'vCPU': specs['vCPU'],
                    'Memory': specs['Memory'],
                    'MonthlyCost': inst_cost,
                    'Savings': savings,
                    'SavingsPercent': savings_percent,
                    'CPUUtilization': vcpu_utilization,
                    'MemoryUtilization': memory_utilization,
                    'Score': savings_percent + (vcpu_utilization * 0.5)  # Prefer better utilization
                })
        
        if not recommendations:
            return None, 0, 0
        
        # Sort by score (savings + utilization)
        recommendations.sort(key=lambda x: x['Score'], reverse=True)
        best = recommendations[0]
        
        return best['InstanceType'], best['Savings'], best['SavingsPercent']
    
    def analyze_instance(self, instance_id, instance_type, region, metrics):
        """Analyze an instance and provide recommendations"""
        cpu_metrics = metrics.get('CPUUtilization', {})
        cpu_avg = cpu_metrics.get('avg', 0) if isinstance(cpu_metrics, dict) else 0
        cpu_max = cpu_metrics.get('max', 0) if isinstance(cpu_metrics, dict) else 0
        
        specs = self.get_instance_specs(instance_type)
        current_cost = self.calculate_monthly_cost(instance_type)
        
        analysis = {
            'InstanceId': instance_id,
            'InstanceType': instance_type,
            'Region': region,
            'CurrentSpecs': specs,
            'CurrentMonthlyCost': current_cost,
            'CPUUsageAvg': cpu_avg,
            'CPUUsageMax': cpu_max,
            'RecommendedType': None,
            'PotentialSavings': 0,
            'SavingsPercent': 0,
            'Recommendation': 'No recommendation available'
        }
        
        if cpu_avg > 0 or cpu_max > 0:
            recommended_type, savings, savings_percent = self.recommend_instance_type(
                instance_type, cpu_avg, cpu_max
            )
            
            analysis['RecommendedType'] = recommended_type
            analysis['PotentialSavings'] = savings
            analysis['SavingsPercent'] = savings_percent
            
            if recommended_type and recommended_type != instance_type:
                if savings > 0:
                    analysis['Recommendation'] = (
                        f"Consider downgrading to {recommended_type} - "
                        f"Potential savings: ${savings:.2f}/month ({savings_percent:.1f}%)"
                    )
                elif savings < 0:
                    analysis['Recommendation'] = (
                        f"Consider upgrading to {recommended_type} - "
                        f"Better performance for ${abs(savings):.2f}/month more"
                    )
            elif cpu_avg < 10:
                analysis['Recommendation'] = (
                    f"Very low CPU usage ({cpu_avg:.1f}%). "
                    f"Consider stopping if not needed or using smaller instance type."
                )
            elif cpu_max > 80:
                analysis['Recommendation'] = (
                    f"High CPU usage detected (max: {cpu_max:.1f}%). "
                    f"Monitor closely and consider upgrading if performance degrades."
                )
            else:
                analysis['Recommendation'] = "Instance size appears appropriate for current usage."
        else:
            analysis['Recommendation'] = "No metrics available. Enable CloudWatch monitoring."
        
        return analysis

