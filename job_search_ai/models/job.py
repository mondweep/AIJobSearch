from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class Job:
    title: str
    company: str
    location: str
    description: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    url: str
    source: str
    posted_date: datetime
    match_score: float = 0.0

    def calculate_match_score(self, profile):
        """
        Calculate how well this job matches the user's profile
        """
        # This will be implemented later with more sophisticated matching logic
        pass
