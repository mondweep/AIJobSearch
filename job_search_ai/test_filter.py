import asyncio
from services.adzuna_service import AdzunaService
from utils.job_filter import JobFilter
from utils.job_summary import JobSummary

async def test_filtered_search():
    adzuna = AdzunaService()
    
    # Comprehensive technology leadership search queries
    search_queries = [
        # Technology Leadership
        {
            "keywords": ["Head of Technology"],
            "locations": ["London"]
        },
        {
            "keywords": ["Head of Cloud"],
            "locations": ["London"]
        },
        {
            "keywords": ["Head of Cyber Security"],
            "locations": ["London"]
        },
        # Program/Project Leadership
        {
            "keywords": ["AI Program Manager"],
            "locations": ["London"]
        },
        {
            "keywords": ["Technology Programme Director"],
            "locations": ["London"]
        },
        # Specific Domain Leadership
        {
            "keywords": ["Cloud Architecture Director"],
            "locations": ["London"]
        },
        {
            "keywords": ["AI Director"],
            "locations": ["London"]
        },
        {
            "keywords": ["CISO"],  # Chief Information Security Officer
            "locations": ["London"]
        }
    ]
    
    # Collect all jobs from different searches
    all_jobs = []
    for query in search_queries:
        print(f"\nSearching for: {query['keywords']} in {query['locations']}")
        jobs = await adzuna.search_jobs(
            keywords=query['keywords'],
            locations=query['locations'],
            min_salary=None
        )
        all_jobs.extend(jobs)
        print(f"Found {len(jobs)} jobs")
    
    print(f"\nTotal jobs collected: {len(all_jobs)}")
    
    # Create summary of all jobs
    print("\nSummary of All Jobs:")
    all_jobs_summary = JobSummary(all_jobs)
    all_jobs_summary.print_summary()
    
    # Define specialized filters
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
        },
        {
            "name": "Contract Technology Leadership",
            "filter": JobFilter(
                min_salary=800,  # Daily rate
                contract_type="contract",
                keywords=["technology", "programme", "director"]
            )
        }
    ]
    
    # Apply each filter and show summaries
    for filter_config in filters:
        print(f"\n{'='*50}")
        print(f"Filter: {filter_config['name']}")
        
        filtered_jobs = filter_config['filter'].filter_jobs(all_jobs)
        print(f"Found {len(filtered_jobs)} matching jobs")
        
        # Print summary for this filter
        filter_summary = JobSummary(filtered_jobs)
        filter_summary.print_summary()
        
        print("\nTop Matches:")
        for i, job in enumerate(filtered_jobs[:3], 1):
            print(f"\nJob {i}:")
            print(f"Title: {job['title']}")
            print(f"Company: {job['company'] or 'Not specified'}")
            print(f"Location: {job['location']}")
            if job.get('salary_min') or job.get('salary_max'):
                print(f"Salary Range: £{job.get('salary_min', 'N/A'):,} - £{job.get('salary_max', 'N/A'):,}")
            else:
                print("Salary: Not specified")
            print(f"Contract: {job.get('contract_type', 'Not specified')} - {job.get('contract_time', 'Not specified')}")
            if job.get('description'):
                print(f"Description Preview: {job['description'][:150]}...")

if __name__ == "__main__":
    asyncio.run(test_filtered_search())
