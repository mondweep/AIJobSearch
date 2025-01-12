from utils.profile_parser import ProfileParser
from utils.job_matcher import JobMatcher

def test_job_matcher():
    # First get profile data
    parser = ProfileParser(
        cv_path='tests/data/Mondweep Chakravorty_CVDetails.pdf',
        skills_path='tests/data/LinkedIn Skills.pdf',
        linkedin_exp_path='tests/data/LinkedInExperience _ Mondweep Chakravorty _ LinkedIn (1).pdf'
    )
    
    # Parse profile data
    profile_data = {
        'skills': parser.parse_cv()['skills'],
        'experiences': parser.parse_cv()['experiences'],
        'skills_data': parser.parse_skills(),
        'linkedin_data': parser.parse_linkedin_experience()
    }
    
    # Create job matcher
    matcher = JobMatcher(profile_data)
    
    # Test with sample jobs
    sample_jobs = [
        {
            'title': 'Head of Technology',
            'description': 'Leading technology transformation using Cloud, AI, and DevOps practices. Experience with AWS and Azure required.',
            'salary': 150000
        },
        {
            'title': 'Technical Program Manager',
            'description': 'Managing technical programs and project delivery. Agile experience required.',
            'salary': 120000
        },
        {
            'title': 'Software Engineer',
            'description': 'Python development with AWS experience.',
            'salary': 100000
        }
    ]
    
    # Score and prioritize jobs
    prioritized_jobs = matcher.prioritize_jobs(sample_jobs)
    
    print("\nJob Matching Results:")
    print("=" * 50)
    for job, score, details in prioritized_jobs:
        print(f"\nJob: {job['title']}")
        print(f"Score: {score:.2f}")
        print("Score Details:")
        for key, value in details.items():
            print(f"  {key}: {value:.2f}")
        print(f"Salary: £{job['salary']:,}")
        print("-" * 30)

if __name__ == "__main__":
    test_job_matcher()
