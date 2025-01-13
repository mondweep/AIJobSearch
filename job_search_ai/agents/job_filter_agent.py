from crewai import Agent
from utils.job_filter import JobFilter, JobFilterInput
from utils.config_loader import ConfigLoader
from utils.profile_parser import ProfileParser
from utils.profile_analyzer import ProfileAnalyzer
from pathlib import Path
import json

class JobFilterAgent:
    def get_agent(self):
        """Return the CrewAI agent"""
        return Agent(
            role='Job Filter Specialist',
            goal='Filter and rank jobs based on profile match and criteria',
            backstory="""You are an expert at analyzing job listings and identifying 
            the most relevant positions based on candidate profile and requirements.""",
            allow_delegation=False,
            tools=[JobFilter()],
            verbose=True
        )

    def __init__(self):
        self.agent = self.get_agent()
        config = ConfigLoader.load_config()
        self.filter_configs = config.get('filters', [])
        
        # Get profile paths from config
        profile_paths = config.get('profile_paths', {})
        base_path = Path(__file__).parent.parent
        
        # Initialize profile parser with paths from config
        self.profile_parser = ProfileParser(
            cv_path=str(base_path / profile_paths.get('cv_template')),
            cv_long_path=str(base_path / profile_paths.get('cv_long')),
            cv_more_path=str(base_path / profile_paths.get('cv_more')),
            skills_path=str(base_path / profile_paths.get('skills')),
            linkedin_posts_path=str(base_path / profile_paths.get('linkedin_posts')),
            linkedin_exp_path=str(base_path / profile_paths.get('linkedin_exp')),
            medium_path=str(base_path / profile_paths.get('medium_profile'))
        )
        
        # Parse all profile data sources
        print("\nAnalyzing Profile Data...")
        
        print("\n1. Analyzing CV...")
        self.cv_data = self.profile_parser.parse_cv()
        if self.cv_data:
            print("Skills found:", self.cv_data.get('skills', []))
            print("Experiences found:", self.cv_data.get('experiences', []))
        
        print("\n2. Analyzing Skills...")
        self.skills_data = self.profile_parser.parse_skills()
        if self.skills_data:
            print("Technical Skills:", self.skills_data.get('technical', []))
            print("Soft Skills:", self.skills_data.get('soft', []))
        
        print("\n3. Analyzing LinkedIn Experience...")
        self.linkedin_data = self.profile_parser.parse_linkedin_experience()
        if self.linkedin_data:
            print("Roles:", self.linkedin_data.get('roles', []))
            print("Companies:", self.linkedin_data.get('companies', []))
        
        print("\n4. Analyzing LinkedIn Posts...")
        self.linkedin_posts_data = self.profile_parser.parse_linkedin_posts()
        
        print("\n5. Analyzing Medium Profile...")
        self.medium_data = self.profile_parser.parse_medium_profile()
        if self.medium_data:
            print("Topics:", self.medium_data.get('topics', []))
            print("Expertise:", self.medium_data.get('expertise', []))
        
        # Combine all profile data
        self.complete_profile_data = {
            'cv': self.cv_data,
            'skills': self.skills_data,
            'linkedin': {
                'experience': self.linkedin_data,
                'posts': self.linkedin_posts_data
            },
            'medium': self.medium_data
        }
        
        # Initialize profile analyzer with combined data
        self.profile_analyzer = ProfileAnalyzer(self.complete_profile_data)
        self.profile_analysis = self.profile_analyzer.analyze_profile()

    def filter_jobs(self, jobs, criteria):
        """Filter jobs based on profile match and given criteria"""
        filtered_results = {}
        
        # Get comprehensive profile analysis
        analysis = self.profile_analysis
        
        # Create filters from config with comprehensive profile data
        for filter_config in self.filter_configs:
            job_filter = JobFilter()
            
            # Directly pass the data without extra JSON encoding
            filtered_jobs = job_filter._run(
                jobs=jobs,
                profile_analysis=analysis
            )
            
            try:
                filtered_jobs = json.loads(filtered_jobs)
                filtered_results[filter_config['name']] = filtered_jobs
                
                print(f"\nFilter: {filter_config['name']}")
                print(f"Found {len(filtered_jobs)} matching jobs")
                print("Top matches:")
                for job in filtered_jobs[:10]:  # Show top 3 matches
                    print(f"\nTitle: {job.get('title')}")
                    print(f"Company: {job.get('company')}")
                    print(f"Profile Match: {job['profile_match_score']:.2%}")
                    print(f"Salary: £{job.get('salary_min', 0):,} - £{job.get('salary_max', 0):,}")
                    print(f"URL: {job.get('url', 'Not available')}")
                    
                    # Add new detailed match analysis
                    if 'match_analysis' in job:
                        print("\nMatch Analysis:")
                        print("Strengths:", job['match_analysis'].get('strengths', []))
                        print("Gaps:", job['match_analysis'].get('gaps', []))
                        print("Recommendations:", job['match_analysis'].get('recommendations', []))
                        print("Key Matching Points:", job['match_analysis'].get('matching_points', []))
            
            except json.JSONDecodeError as e:
                print(f"Error decoding filter results: {str(e)}")
                filtered_results[filter_config['name']] = []
        
        return filtered_results
