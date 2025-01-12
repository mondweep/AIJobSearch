import os
import aiohttp
from dotenv import load_dotenv

class AdzunaService:
    def __init__(self):
        load_dotenv()
        self.app_id = os.getenv('ADZUNA_APP_ID')
        self.api_key = os.getenv('ADZUNA_API_KEY')
        self.country = 'gb'  # Default to UK
        self.base_url = "http://api.adzuna.com/v1/api/jobs/{}/search/1"

    def set_country(self, country_code):
        """Set the country for job searches"""
        self.country = country_code.lower()  # Ensure lowercase
        return self

    async def search_jobs(self, keywords, locations, min_salary):
        """
        Search for jobs using the Adzuna API
        """
        # Format keywords for search
        keyword_string = " ".join(keywords)
        
        params = {
            'app_id': self.app_id,
            'app_key': self.api_key,
            'results_per_page': 20,
            'what': keyword_string,
            'content-type': 'application/json',
        }

        # Add location if provided
        if locations and locations[0]:
            params['where'] = locations[0]

        # Add salary if provided
        if min_salary:
            params['salary_min'] = min_salary

        try:
            url = self.base_url.format(self.country)
            print(f"Making request to {url}")  # Debug line
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    print(f"Response Status: {response.status}")
                    
                    if response.status == 200:
                        data = await response.json()
                        print(f"Total results found: {data.get('count', 0)}")
                        return self._parse_jobs(data)
                    else:
                        error_text = await response.text()
                        print(f"Error response: {error_text}")
                        raise Exception(f"Adzuna API error: Status {response.status}, {error_text}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")

    def _parse_jobs(self, data):
        """Parse the raw API response into our job model format"""
        jobs = []
        results = data.get('results', [])
        
        for job in results:
            location = job.get('location', {})
            area = location.get('area', [])
            location_display = location.get('display_name', '')
            
            parsed_job = {
                'title': job.get('title'),
                'company': job.get('company', {}).get('display_name'),
                'location': location_display,
                'area': area,
                'description': job.get('description'),
                'salary_min': job.get('salary_min'),
                'salary_max': job.get('salary_max'),
                'url': job.get('redirect_url'),
                'source': 'Adzuna',
                'posted_date': job.get('created'),
                'category': job.get('category', {}).get('label'),
                'contract_type': job.get('contract_type'),
                'contract_time': job.get('contract_time')
            }
            jobs.append(parsed_job)
        return jobs
