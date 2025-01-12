from crewai import Agent
from utils.job_filter import JobFilter

class JobFilterAgent:
    def get_agent(self):
        """Return the CrewAI agent"""
        return Agent(
            role='Job Filter Specialist',
            goal='Filter and rank jobs based on specific criteria',
            backstory="""You are an expert at analyzing job listings and identifying 
            the most relevant positions based on salary, skills, and requirements.""",
            allow_delegation=False,
            verbose=True
        )

    def __init__(self):
        self.agent = self.get_agent()

    def filter_jobs(self, jobs, criteria):
        """
        Filter jobs based on given criteria
        """
        filters = [
            {
                "name": "High Salary Technology Leadership",
                "filter": JobFilter(
                    min_salary=140000,
                    keywords=["head", "director", "technology", "cloud", "security"]
                )
            },
            {
                "name": "AI and Machine Learning Leadership",
                "filter": JobFilter(
                    min_salary=120000,
                    keywords=["ai", "artificial intelligence", "machine learning"]
                )
            },
            {
                "name": "Cloud and Security Leadership",
                "filter": JobFilter(
                    min_salary=120000,
                    keywords=["cloud", "security", "cyber"]
                )
            }
        ]

        filtered_results = {}
        for filter_config in filters:
            filtered_jobs = filter_config["filter"].filter_jobs(jobs)
            filtered_results[filter_config["name"]] = filtered_jobs

        return filtered_results
