from crewai import Crew, Task
from agents.job_search_agent import JobSearchAgent
from agents.job_filter_agent import JobFilterAgent
from agents.job_analyst_agent import JobAnalystAgent

class JobSearchCrew:
    def __init__(self):
        # Initialize agents
        self.search_agent = JobSearchAgent()
        self.filter_agent = JobFilterAgent()
        self.analyst_agent = JobAnalystAgent()

    def get_crew(self, search_criteria):
        """Create and return the crew"""
        return Crew(
            agents=[
                self.search_agent.agent,
                self.filter_agent.agent,
                self.analyst_agent.agent
            ],
            tasks=[
                Task(
                    description=f"""Search for technology leadership positions with the following criteria:
                    Positions: {search_criteria['positions']}
                    Locations: {search_criteria['locations']}
                    Minimum Salary: £{search_criteria['min_salary']:,}""",
                    agent=self.search_agent.agent,
                    expected_output="A list of job postings matching the search criteria"
                ),
                Task(
                    description="Filter and rank the found jobs based on salary and requirements",
                    agent=self.filter_agent.agent,
                    expected_output="A filtered and ranked list of jobs with salary and requirement matches"
                ),
                Task(
                    description="Analyze job market trends and provide detailed insights",
                    agent=self.analyst_agent.agent,
                    expected_output="A detailed analysis of job market trends including salary ranges and recommendations"
                )
            ]
        )

    async def run(self, search_criteria):
        """Execute the crew's tasks"""
        crew = self.get_crew(search_criteria)
        result = await crew.kickoff()
        return result
