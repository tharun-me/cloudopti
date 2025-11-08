"""Cost-saving recommendations engine"""


class RecommendationsEngine:
    """Generate cost-saving recommendations based on cost data"""
    
    def generate(self, costs_by_service, total_cost):
        """Generate recommendations based on cost breakdown"""
        recommendations = []
        
        if not costs_by_service:
            return recommendations
        
        # Find top cost services
        sorted_services = sorted(costs_by_service.items(), key=lambda x: x[1], reverse=True)
        top_service = sorted_services[0]
        
        # Recommendation 1: Top cost service
        if top_service[1] > 50:  # If top service costs more than $50
            recommendations.append(
                f"{top_service[0]} is your highest cost (${top_service[1]:.2f}). "
                f"Review usage and consider optimization."
            )
        
        # Recommendation 2: EC2 specific
        if 'Amazon Elastic Compute Cloud - Compute' in costs_by_service:
            ec2_cost = costs_by_service['Amazon Elastic Compute Cloud - Compute']
            if ec2_cost > 30:
                recommendations.append(
                    f"EC2 costs ${ec2_cost:.2f}. Consider stopping unused instances, "
                    f"using Reserved Instances for steady workloads, or switching to "
                    f"Spot Instances for fault-tolerant applications."
                )
        
        # Recommendation 3: S3 specific
        if 'Amazon Simple Storage Service' in costs_by_service:
            s3_cost = costs_by_service['Amazon Simple Storage Service']
            if s3_cost > 20:
                recommendations.append(
                    f"S3 costs ${s3_cost:.2f}. Review storage classes - move infrequently "
                    f"accessed data to S3 Glacier or S3 Intelligent-Tiering for automatic "
                    f"cost optimization."
                )
        
        # Recommendation 4: RDS specific
        if 'Amazon Relational Database Service' in costs_by_service:
            rds_cost = costs_by_service['Amazon Relational Database Service']
            if rds_cost > 30:
                recommendations.append(
                    f"RDS costs ${rds_cost:.2f}. Consider Reserved Instances for "
                    f"production databases, or review if all databases are actively used."
                )
        
        # Recommendation 5: Lambda specific
        if 'AWS Lambda' in costs_by_service:
            lambda_cost = costs_by_service['AWS Lambda']
            if lambda_cost > 10:
                recommendations.append(
                    f"Lambda costs ${lambda_cost:.2f}. Review function memory allocation "
                    f"and execution time - over-provisioned memory increases costs."
                )
        
        # Recommendation 6: General optimization
        if total_cost > 100:
            recommendations.append(
                f"Total monthly cost is ${total_cost:.2f}. Consider setting up AWS Budgets "
                f"to track spending and receive alerts when thresholds are exceeded."
            )
        
        # Recommendation 7: Multiple services
        if len(costs_by_service) > 10:
            recommendations.append(
                f"You're using {len(costs_by_service)} different services. Review each "
                f"service's usage - unused or underutilized resources can be terminated "
                f"to reduce costs."
            )
        
        # Recommendation 8: Low cost services
        low_cost_services = [s for s, c in costs_by_service.items() if c < 5]
        if len(low_cost_services) > 5:
            recommendations.append(
                f"Multiple services with low costs detected. Consider consolidating "
                f"functionality to reduce service sprawl and simplify management."
            )
        
        # If no specific recommendations, provide general advice
        if not recommendations:
            recommendations.append(
                "Your AWS costs are relatively low. Continue monitoring to catch "
                "cost increases early."
            )
        
        return recommendations

