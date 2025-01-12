class JobFilter:
    def __init__(self, min_salary=None, contract_type=None, keywords=None):
        self.min_salary = min_salary
        self.contract_type = contract_type
        self.keywords = keywords or []

    def filter_jobs(self, jobs):
        """Filter jobs based on criteria and remove duplicates"""
        filtered_jobs = []
        seen_jobs = set()  # Track unique jobs
        
        for job in jobs:
            # Create a unique identifier for the job using title, company, and salary
            job_id = (
                job.get('title', ''),
                job.get('company', ''),
                job.get('salary_min', 0),
                job.get('salary_max', 0)
            )
            
            # Skip if we've seen this combination before
            if job_id in seen_jobs:
                continue
                
            if self.meets_criteria(job):
                filtered_jobs.append(job)
                seen_jobs.add(job_id)
                
        # Sort by maximum salary first, then minimum salary
        return sorted(
            filtered_jobs,
            key=lambda x: (
                x.get('salary_max', 0) or x.get('salary_min', 0) or 0,
                x.get('salary_min', 0) or 0
            ),
            reverse=True
        )

    def meets_criteria(self, job):
        """Check if job meets all criteria"""
        try:
            # Check minimum salary
            if self.min_salary:
                max_salary = job.get('salary_max', 0) or 0
                min_salary = job.get('salary_min', 0) or 0
                job_salary = max(max_salary, min_salary)
                if job_salary < self.min_salary:
                    return False

            # Check contract type
            if self.contract_type:
                job_contract = (job.get('contract_type') or '').lower()
                if not job_contract:  # Skip if contract type is missing
                    return False
                if job_contract != self.contract_type.lower():
                    return False

            # Check keywords in title or description
            if self.keywords:
                text_to_search = (
                    f"{job.get('title', '')} {job.get('description', '')} "
                    f"{job.get('company', '')}"
                ).lower()
                if not all(keyword.lower() in text_to_search for keyword in self.keywords):
                    return False

            return True
            
        except Exception as e:
            print(f"Error processing job: {str(e)}")
            return False
