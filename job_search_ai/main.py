import asyncio
from job_search_crew import JobSearchCrew
from dotenv import load_dotenv

async def main():
    # Load environment variables
    load_dotenv()
    
    # Initialize the crew
    crew = JobSearchCrew()
    
    # Define search criteria
    search_criteria = {
        "positions": [
            "Head of Technology",
            "Head of Cloud",
            "Head of Cyber Security",
            "AI Program Manager"
        ],
        "locations": ["London"],
        "min_salary": 140000,
        "contract_types": ["permanent", "contract"]
    }
    
    try:
        # Run the crew
        print("Starting job search crew...")
        crew_instance = crew.get_crew(search_criteria)
        results = crew_instance.kickoff()
        
        # Print results
        print("\nJob Search Results:")
        print("=" * 50)
        print(results)
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())
