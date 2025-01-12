import os
import aiohttp
from dotenv import load_dotenv

class JobserveService:
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('JOBSERVE_API_KEY')
        self.base_url = "https://www.jobserve.com/api/search"

    async def search_jobs(self, keywords, locations, min_salary):
        """
        Search for jobs using the JobServe API
        """
        params = {
            'api_key': self.api_key,
            'keywords': ' OR '.join(keywords),
            'salary_min': min_salary,
            'format': 'json',
            'page_size': 50
        }

        # Handle multiple locations
        if locations:
            params['locations'] = ' OR '.join(locations)

        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return self._parse_jobs(data)
                else:
                    error_text = await response.text()
                    raise Exception(f"JobServe API error: {error_text}")

    def _parse_jobs(self, data):
        """
        Parse the raw API response into our job model format
        """
        jobs = []
        for job in data.get('jobs', []):
            parsed_job = {
                'title': job.get('title'),
                'company': job.get('company'),
                'location': job.get('location'),
                'description': job.get('description'),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'url': job.get('url'),
                'source': 'JobServe',
                'posted_date': job.get('posted_date')
            }
            jobs.append(parsed_job)
        return jobs
