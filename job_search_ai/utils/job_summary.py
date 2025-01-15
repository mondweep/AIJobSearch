class JobSummary:
    def __init__(self, jobs):
        self.jobs = jobs

    def get_salary_stats(self):
        """Calculate salary statistics"""
        salaries = []
        for job in self.jobs:
            max_salary = job.get('salary_max', 0) or 0
            min_salary = job.get('salary_min', 0) or 0
            if max_salary or min_salary:
                avg_salary = (max_salary + min_salary) / 2 if max_salary and min_salary else max_salary or min_salary
                salaries.append(avg_salary)
        
        if not salaries:
            return None
            
        return {
            'min': min(salaries),
            'max': max(salaries),
            'avg': sum(salaries) / len(salaries),
            'count': len(salaries)
        }

    def get_top_companies(self, limit=5):
        """Get companies with the most openings"""
        companies = {}
        for job in self.jobs:
            company = job.get('company')
            if company:
                companies[company] = companies.get(company, 0) + 1
        
        return sorted(
            companies.items(),
            key=lambda x: x[1],
            reverse=True
        )[:limit]

    def get_contract_distribution(self):
        """Get distribution of contract types"""
        contracts = {}
        for job in self.jobs:
            contract = job.get('contract_type', 'Not specified')
            contracts[contract] = contracts.get(contract, 0) + 1
        return contracts

    def print_summary(self):
        """Print a formatted summary of the jobs"""
        print("\nJob Market Summary")
        print("=" * 50)
        
        # Salary Statistics
        stats = self.get_salary_stats()
        if stats:
            print("\nSalary Statistics:")
            print(f"Range: £{stats['min']:,.2f} - £{stats['max']:,.2f}")
            print(f"Average: £{stats['avg']:,.2f}")
            print(f"Jobs with salary info: {stats['count']}")
        
        # Contract Types
        print("\nContract Types:")
        for contract, count in self.get_contract_distribution().items():
            print(f"{contract}: {count} positions")
        
        # Top Companies
        print("\nTop Companies:")
        for company, count in self.get_top_companies():
            print(f"{company}: {count} positions")
