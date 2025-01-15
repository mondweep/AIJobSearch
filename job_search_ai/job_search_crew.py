from crewai import Crew, Agent, Task
from services.adzuna_service import AdzunaService
from utils.config_loader import ConfigLoader
from utils.profile_parser import ProfileParser
from utils.job_matcher import JobMatcher
from utils.job_filter import JobFilter
from agents.job_search_agent import JobSearchAgent
from agents.job_filter_agent import JobFilterAgent
from agents.job_analyst_agent import JobAnalystAgent
from utils.profile_analyzer import ProfileAnalyzer
from agents.job_search_agent import JobSearchTool
from utils.job_filter import JobFilter
from pathlib import Path

class JobSearchCrew:
    def __init__(self):
        # Load config and store it
        self.config = ConfigLoader.load_config()
        profile_paths = self.config.get('profile_paths', {})
        base_path = Path(__file__).parent
        
        print("\nDebug: Profile Analysis Flow:")
        
        # Initialize profile parser with safe path handling
        parser_args = {
            'cv_path': str(base_path / profile_paths['cv_template']) if profile_paths.get('cv_template') else None,
            'cv_long_path': str(base_path / profile_paths['cv_long']) if profile_paths.get('cv_long') else None,
            'cv_more_path': str(base_path / profile_paths['cv_more']) if profile_paths.get('cv_more') else None,
            'skills_path': str(base_path / profile_paths['skills']) if profile_paths.get('skills') else None,
            'linkedin_posts_path': str(base_path / profile_paths['linkedin_posts']) if profile_paths.get('linkedin_posts') else None,
            'linkedin_exp_path': str(base_path / profile_paths['linkedin_exp']) if profile_paths.get('linkedin_exp') else None,
            'linkedin_positions_path': str(base_path / profile_paths['positions']) if profile_paths.get('positions') else None,
            'linkedin_profile_path': str(base_path / profile_paths['linkedin_profile']) if profile_paths.get('linkedin_profile') else None,
            'linkedin_certifications_path': str(base_path / profile_paths['certification']) if profile_paths.get('certification') else None,
            'linkedin_education_path': str(base_path / profile_paths['education']) if profile_paths.get('education') else None,
            'linkedin_endorsements_path': str(base_path / profile_paths['endorsements']) if profile_paths.get('endorsements') else None,
            'linkedin_articles_path': str(base_path / profile_paths['linkedin_articles']) if profile_paths.get('linkedin_articles') else None,
            'medium_path': str(base_path / profile_paths['medium_profile']) if profile_paths.get('medium_profile') else None
        }
        
        # Initialize profile parser
        self.profile_parser = ProfileParser(**parser_args)
        
        # Parse all profile data
        print("\n1. Parsing Profile Data...")
        cv_data = self.profile_parser.parse_cv()
        skills_data = self.profile_parser.parse_skills()
        
        # Replace the direct linkedin_experience call with complete linkedin_data parsing
        print("\n=== Parsing LinkedIn Data ===")
        linkedin_data = self.profile_parser.parse_linkedin_data()  # This will parse all LinkedIn components
        
        medium_data = self.profile_parser.parse_medium_profile()
        
        # Combine all profile data
        print("\n2. Combining Profile Data...")
        self.complete_profile_data = {
            'cv': cv_data,
            'skills': skills_data,
            'linkedin': linkedin_data,  # This now contains all LinkedIn components
            'medium': medium_data
        }
        
        # Debug output for LinkedIn components
        if linkedin_data:
            print("\nLinkedIn Components Found:")
            print(f"- Profile: {'Present' if linkedin_data.get('profile') else 'Missing'}")
            print(f"- Experience: {len(linkedin_data.get('experience', []))} entries")
            print(f"- Posts: {len(linkedin_data.get('posts', []))} entries")
            print(f"- Articles: {len(linkedin_data.get('articles', []))} entries")
            print(f"- Endorsements: {len(linkedin_data.get('endorsements', {}))} skills")
            print(f"- Certifications: {len(linkedin_data.get('certifications', []))} entries")
            print(f"- Education: {len(linkedin_data.get('education', []))} entries")
        
        print(f"Combined data keys: {self.complete_profile_data.keys()}")
        
        # Initialize profile analyzer with combined data
        print("\n3. Analyzing Profile...")
        self.profile_analyzer = ProfileAnalyzer(self.complete_profile_data)
        self.profile_analysis = self.profile_analyzer.analyze_profile()
        print(f"Analysis result keys: {self.profile_analysis.keys() if self.profile_analysis else 'None'}")
        
        # Store the analyzed profile data
        print("\n4. Storing Profile Data...")
        self.profile_data = {
            'raw_data': self.complete_profile_data,
            'analysis': self.profile_analysis
        }
        print(f"Final profile_data keys: {self.profile_data.keys()}")
        
        # Get filter configs
        self.filters = self.config.get('filters', [])
        
        # Initialize other attributes
        self.job_data = None
        
        # Initialize job matcher
        self.job_matcher = JobMatcher(self.complete_profile_data)
        
        # Initialize filters from config
        self.job_filters = [
            JobFilter(
                min_salary=filter_config['min_salary'],
                contract_type=filter_config.get('contract_type'),
                keywords=filter_config.get('keywords', [])
            )
            for filter_config in self.filters
        ]
        
        # Update profile data with detailed analysis
        self.complete_profile_data.update({
            'analysis': self.profile_analysis
        })

    def get_agents(self):
        """Create and return the agents needed for the job search"""
        
        # First create the filter agent without tools
        filter_agent = Agent(
            role='Job Filter Specialist',
            goal='Filter and rank jobs based on profile match and criteria',
            backstory="""You are an expert at analyzing job listings and identifying 
                     the most relevant positions based on candidate profile and requirements.""",
            allow_delegation=False,
            verbose=True
        )
        
        # Create JobFilter tool with agent reference
        job_filter = JobFilter(
            agent=filter_agent,
            min_salary=self.config.get('search_criteria', {}).get('salary', {}).get('min'),
            contract_type=self.config.get('search_criteria', {}).get('contract_type'),
            keywords=self.config.get('search_criteria', {}).get('keywords', [])
        )
        
        # Update filter agent with tools
        filter_agent.tools = [job_filter]
        
        # Job Search Agent with rich definition
        search_agent = Agent(
            role='Job Search Specialist',
            goal='Find relevant job opportunities based on search criteria',
            backstory="""You are an expert at finding job opportunities that match 
                     specific requirements and criteria.""",
            allow_delegation=False,
            tools=[JobSearchTool()],
            verbose=True
        )
        
        # Job Analysis Agent with rich definition
        analyst_agent = Agent(
            role='Job Analysis Specialist',
            goal='Analyze job matches and provide detailed career recommendations',
            backstory="""You are an expert at analyzing job opportunities, evaluating matches 
                     between candidate profiles and job requirements, and providing strategic 
                     career guidance. You excel at identifying both obvious and subtle matches 
                     between skills and job requirements.""",
            allow_delegation=False,
            verbose=True
        )

        return [search_agent, filter_agent, analyst_agent]

    def process_jobs(self, jobs):
        """Process jobs through filtering and matching"""
        results = {}
        
        # Apply filters from config
        print("\nApplying filters...")
        for job_filter in self.job_filters:
            filtered_jobs = job_filter.filter_jobs(jobs)
            if filtered_jobs:
                results[f"Filter: {job_filter.__class__.__name__}"] = filtered_jobs
        
        # Score and rank filtered jobs
        print("\nScoring and ranking jobs...")
        all_filtered_jobs = [job for sublist in results.values() for job in sublist]
        scored_jobs = self.job_matcher.prioritize_jobs(all_filtered_jobs)
        
        return {
            'filtered_results': results,
            'scored_jobs': scored_jobs
        }

    def create_tasks(self, agents):
        """Create tasks for the agents"""
        search_agent, filter_agent, analyst_agent = agents
        
        # Debug the profile data structure
        print("\nDebug - Profile Data Structure:")
        print(f"Complete profile data: {self.complete_profile_data}")
        print(f"Profile analysis: {self.profile_analysis}")
        
        # Get search criteria from config
        search_criteria = self.config.get('search_criteria', {})
        positions = search_criteria.get('positions', [])
        
        print("\nDebug: Creating tasks with profile data...")
        print(f"Profile data available: {self.profile_data is not None}")
        if self.profile_data:
            print(f"Profile data keys: {self.profile_data.keys()}")
        
        # Task 1: Search for jobs
        search_task = Task(
            description=f"""Search for jobs with these criteria:
            Positions: {positions}
            Locations: {search_criteria.get('locations', [])}
            Minimum Salary: {search_criteria.get('salary', {}).get('min')} {search_criteria.get('salary', {}).get('currency')}
            Contract Types: {search_criteria.get('contract_types', [])}""",
            agent=search_agent,
            expected_output="List of job opportunities matching the search criteria"
        )
        
        # Task 2: Filter and rank jobs
        filter_task = Task(
            description=f"""Filter and rank the jobs based on:
            1. Apply configured filters
            2. Calculate profile match scores
            3. Sort by relevance and salary
            Use both the job filters and matcher to process the jobs.
            Profile Analysis: {self.profile_analysis}""",
            agent=filter_agent,
            expected_output="Filtered and ranked list of jobs with match scores"
        )

        # Task 3: Analyze results
        analysis_task = Task(
            description="""Analyze the filtered and ranked jobs:
            1. Top matching positions
            2. Salary ranges
            3. Required skills analysis
            4. Recommendations for profile improvements""",
            agent=analyst_agent,
            expected_output="Detailed analysis of job matches and recommendations"
        )

        return [search_task, filter_task, analysis_task]

    def run(self):
        """Run the job search crew"""
        # Create agents
        agents = self.get_agents()
        
        # Create tasks
        tasks = self.create_tasks(agents)
        
        # Create crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=True
        )
        
        # Start the crew
        result = crew.kickoff()
        
        return result

    def format_job_details(self, job):
        """Format job details including URL"""
        return f"""
Job Details:
Title: {job.get('title')}
Company: {job.get('company')}
Location: {job.get('location', 'Not specified')}
URL: {job.get('url', 'Not available')}

Description:
{job.get('description')}

Requirements:
{job.get('requirements', 'Not specified')}

-------------------
"""

if __name__ == "__main__":
    crew = JobSearchCrew()
    result = crew.run()
    print("\nJob Search Results:")
    print(result)
