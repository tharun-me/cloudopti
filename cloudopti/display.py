"""Display utilities for showing cost data"""

from tabulate import tabulate


class DisplayTable:
    """Handle table display for cost data"""
    
    def show_table(self, costs_by_service, total_cost):
        """Display costs in a formatted table"""
        # Prepare table data
        table_data = []
        for service, cost in costs_by_service.items():
            table_data.append([service, f"${cost:.2f}"])
        
        # Add total row
        table_data.append(["─" * 20, "─" * 10])
        table_data.append(["TOTAL", f"${total_cost:.2f}"])
        
        # Display table
        headers = ["Service", "Cost ($)"]
        print("\n" + tabulate(table_data, headers=headers, tablefmt="grid"))

