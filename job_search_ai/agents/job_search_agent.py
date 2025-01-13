from crewai import Agent
from utils.job_search_tool import JobSearchTool
from utils.config_loader import ConfigLoader

class JobSearchAgent:
    def get_agent(self):
        """Return the CrewAI agent"""
        return Agent(
            role='Job Search Specialist',
            goal='Find the most relevant high-paying technology leadership positions',
            backstory="You are an expert at finding technology leadership positions. "
                     "You understand various job titles and their market values.",
            allow_delegation=False,
            tools=[JobSearchTool()],
            verbose=True
        )
    def __init__(self):
        self.adzuna_service = AdzunaService()
        self.agent = self.get_agent()
        self.config = ConfigLoader.load_config()

    async def execute_search(self, search_criteria):
        """
        Execute job search based on given criteria
        """
        config = self.config['search_criteria']
        
        # Create search queries from config
        search_queries = [
            {
                "keywords": [position],
                "locations": config['locations']
            }
            for position in config['positions']
        ]
        
        all_jobs = []
        for query in search_queries:
            jobs = await self.adzuna_service.search_jobs(
                keywords=query["keywords"],
                locations=query["locations"],
                min_salary=config['salary'].get('min')
            )
            # Ensure each job has a URL
            for job in jobs:
                if 'redirect_url' in job:
                    job['url'] = job['redirect_url']
                elif 'adref' in job:
                    job['url'] = f"https://www.adzuna.co.uk/jobs/details/{job['adref']}"
                else:
                    job['url'] = "URL not available"
            all_jobs.extend(jobs)
            
        return all_jobs

