from difflib import SequenceMatcher

class JobMatcher:
    def __init__(self, profile_data):
        """
        Initialize with parsed profile data
        profile_data should contain:
        - skills (technical and soft)
        - experiences (roles)
        """
        self.profile_data = profile_data
        self.skills = self._get_all_skills()
        self.experiences = self._get_all_experiences()

    def _get_all_skills(self):
        """Combine all skills from profile data"""
        skills = set()
        if 'skills' in self.profile_data:
            skills.update(self.profile_data['skills'])
        if 'technical' in self.profile_data.get('skills_data', {}):
            skills.update(self.profile_data['skills_data']['technical'])
        if 'soft' in self.profile_data.get('skills_data', {}):
            skills.update(self.profile_data['skills_data']['soft'])
        return list(skills)

    def _get_all_experiences(self):
        """Get all experience/roles from profile data"""
        experiences = set()
        if 'experiences' in self.profile_data:
            experiences.update(self.profile_data['experiences'])
        if 'roles' in self.profile_data.get('linkedin_data', {}):
            experiences.update(self.profile_data['linkedin_data']['roles'])
        return list(experiences)

    def score_job(self, job):
        """
        Score a job based on how well it matches the profile
        Returns a score between 0 and 1
        """
        scores = {
            'title_match': self._score_title_match(job.get('title', '')),
            'skills_match': self._score_skills_match(job.get('description', '')),
            'experience_match': self._score_experience_match(job.get('description', ''))
        }

        # Weighted average of scores
        weights = {
            'title_match': 0.4,
            'skills_match': 0.4,
            'experience_match': 0.2
        }

        final_score = sum(score * weights[key] for key, score in scores.items())
        return final_score, scores

    def _score_title_match(self, job_title):
        """Score how well the job title matches past roles"""
        return max(
            SequenceMatcher(None, job_title.lower(), exp.lower()).ratio()
            for exp in self.experiences
        )

    def _score_skills_match(self, job_description):
        """Score how many required skills match"""
        if not job_description or not self.skills:
            return 0
        
        matched_skills = sum(
            1 for skill in self.skills
            if skill.lower() in job_description.lower()
        )
        return min(matched_skills / len(self.skills), 1.0)

    def _score_experience_match(self, job_description):
        """Score how well experience matches"""
        if not job_description or not self.experiences:
            return 0
        
        matched_exp = sum(
            1 for exp in self.experiences
            if exp.lower() in job_description.lower()
        )
        return min(matched_exp / len(self.experiences), 1.0)

    def prioritize_jobs(self, jobs):
        """
        Score and sort jobs by relevance
        Returns list of (job, score, score_details) tuples
        """
        scored_jobs = []
        for job in jobs:
            score, score_details = self.score_job(job)
            scored_jobs.append((job, score, score_details))
        
        # Sort by score descending
        return sorted(scored_jobs, key=lambda x: x[1], reverse=True)
