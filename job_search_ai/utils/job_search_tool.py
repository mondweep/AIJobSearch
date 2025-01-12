from crewai.tools import BaseTool
from services.adzuna_service import AdzunaService
from typing import List, Dict, Any
from pydantic import Field, ConfigDict
import asyncio
import re

class JobSearchTool(BaseTool):
    """Tool for searching jobs using Adzuna API"""
    
    name: str = "Job Search Tool"
    description: str = "Search for jobs using specific criteria like keywords, locations, and minimum salary"
    adzuna_service: AdzunaService = Field(default_factory=AdzunaService, exclude=True)

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _run(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute the job search"""
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        return loop.run_until_complete(self._async_run(criteria))

    def _format_job_url(self, job: Dict[str, Any]) -> str:
        """Format the job URL correctly"""
        # If we have an ID and title, create a SEO-friendly URL
        if 'id' in job and 'title' in job:
            # Clean the title for URL
            clean_title = re.sub(r'[^a-zA-Z0-9]+', '_', job['title'])
            return f"https://www.adzuna.co.uk/jobs/details/{job['id']}?title={clean_title}"
        # If we have redirect_url, use it
        elif 'redirect_url' in job:
            return job['redirect_url']
        # If we have adref, use that
        elif 'adref' in job:
            return f"https://www.adzuna.co.uk/jobs/details/{job['adref']}"
        # Fallback
        return "URL not available"

    async def _async_run(self, criteria: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Async implementation of job search"""
        try:
            # Extract search parameters
            search_params = criteria.get('description', {})
            if not search_params:
                search_params = criteria  # fallback to direct parameters

            # Get all positions to search for
            positions = search_params.get('positions', [])
            if not positions:
                return []

            all_jobs = []
            # Search for each position
            for position in positions:
                try:
                    jobs = await self.adzuna_service.search_jobs(
                        keywords=[position],
                        locations=search_params.get('locations', []),
                        min_salary=search_params.get('minimum_salary')
                    )

                    # Process URLs
                    for job in jobs:
                        job['url'] = self._format_job_url(job)
                    
                    all_jobs.extend(jobs)
                    print(f"Found {len(jobs)} jobs for position: {position}")
                except Exception as e:
                    print(f"Error searching for position {position}: {str(e)}")
                    continue
            
            print(f"Total jobs found across all positions: {len(all_jobs)}")
            return all_jobs

        except Exception as e:
            print(f"Error in job search: {str(e)}")
            return []
