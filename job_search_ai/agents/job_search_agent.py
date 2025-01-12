from crewai import Agent
from services.adzuna_service import AdzunaService

class JobSearchAgent:
    def get_agent(self):
        """Return the CrewAI agent"""
        return Agent(
            role='Job Search Specialist',
            goal='Find the most relevant high-paying technology leadership positions',
            backstory="""You are an expert at finding technology leadership positions.
            You understand various job titles and their market values.""",
            allow_delegation=False,
            verbose=True
        )

    def __init__(self):
        self.adzuna_service = AdzunaService()
        self.agent = self.get_agent()

    async def execute_search(self, search_criteria):
        """
        Execute job search based on given criteria
        """
        search_queries = [
            {
                "keywords": ["Head of Technology", "Technology Director"],
                "locations": ["London"]
            },
            {
                "keywords": ["Head of Cloud", "Cloud Director"],
                "locations": ["London"]
            },
            {
                "keywords": ["CISO", "Head of Cyber Security"],
                "locations": ["London"]
            }
        ]
        
        all_jobs = []
        for query in search_queries:
            jobs = await self.adzuna_service.search_jobs(
                keywords=query["keywords"],
                locations=query["locations"],
                min_salary=None
            )
            all_jobs.extend(jobs)
            
        return all_jobs
