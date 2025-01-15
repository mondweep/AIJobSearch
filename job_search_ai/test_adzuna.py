import asyncio
from services.adzuna_service import AdzunaService

async def test_adzuna_search():
    adzuna = AdzunaService()
    
    test_cases = [
        {
            # Test Case 1: Program Director in London
            "keywords": ["Program Director"],
            "locations": ["London"],
            "min_salary": None,
            "country": "gb"
        },
        {
            # Test Case 2: Technical Program Manager in London
            "keywords": ["Technical Program Manager"],
            "locations": ["London"],
            "min_salary": None,
            "country": "gb"
        },
        {
            # Test Case 3: Programme Director (UK spelling)
            "keywords": ["Programme Director"],
            "locations": ["London"],
            "min_salary": None,
            "country": "gb"
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"Test Case {i}:")
        print(f"Keywords: {test_case['keywords']}")
        print(f"Location: {test_case['locations']}")
        print(f"Country: {test_case['country'].upper()}")
        
        try:
            adzuna.set_country(test_case['country'])
            jobs = await adzuna.search_jobs(
                keywords=test_case['keywords'],
                locations=test_case['locations'],
                min_salary=test_case['min_salary']
            )
            
            print(f"\nFound {len(jobs)} jobs")
            
            if len(jobs) > 0:
                print("\nTop matches:")
                # Sort jobs, handling None values safely
                sorted_jobs = sorted(
                    jobs,
                    key=lambda x: (x.get('salary_max', 0) or 0) + (x.get('salary_min', 0) or 0),
                    reverse=True
                )
                
                for j, job in enumerate(sorted_jobs[:5], 1):
                    print(f"\nJob {j}:")
                    print(f"Title: {job['title']}")
                    print(f"Company: {job['company'] or 'Not specified'}")
                    print(f"Location: {job['location']}")
                    if job.get('salary_min') or job.get('salary_max'):
                        if test_case['country'] == 'gb':
                            print(f"Salary Range: £{job.get('salary_min', 'N/A'):,} - £{job.get('salary_max', 'N/A'):,}")
                        else:
                            print(f"Salary Range: {job.get('salary_min', 'N/A'):,} - {job.get('salary_max', 'N/A'):,}")
                    else:
                        print("Salary: Not specified")
                    if job.get('description'):
                        print(f"Description Preview: {job['description'][:150]}...")
                    print(f"Contract: {job.get('contract_type', 'Not specified')} - {job.get('contract_time', 'Not specified')}")
                
        except Exception as e:
            print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_adzuna_search())
