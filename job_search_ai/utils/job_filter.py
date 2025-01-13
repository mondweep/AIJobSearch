from crewai.tools import BaseTool
from typing import List, Dict, Any, Optional, Type
from pydantic import BaseModel, Field
import json

class JobFilterInput(BaseModel):
    jobs: List[Dict[str, Any]] = Field(description="List of jobs to filter")
    profile_analysis: Dict[str, Any] = Field(description="Profile analysis data")

class JobFilter(BaseTool):
    """Tool for filtering and ranking jobs"""
    name: str = Field(default="Job Filter")
    description: str = Field(default="Filter and rank jobs based on profile match and criteria")
    agent: Optional[Any] = Field(default=None)
    min_salary: Optional[float] = Field(default=None)
    contract_type: Optional[str] = Field(default=None)
    keywords: Optional[List[str]] = Field(default_factory=list)

    def __init__(self, agent=None, min_salary=None, contract_type=None, keywords=None):
        super().__init__()
        self.agent = agent
        self.min_salary = min_salary
        self.contract_type = contract_type
        self.keywords = keywords if keywords else []

    def _run(self, jobs: List[Dict[str, Any]], profile_analysis: Dict[str, Any]) -> str:
        """Required method for CrewAI Tool"""
        try:
            # Debug the incoming data
            print("Profile Analysis Structure:", json.dumps(profile_analysis, indent=2))
            
            # Keep original profile data while adding formatted structure
            enhanced_profile = {
                **profile_analysis,  # Preserve all original data
                'formatted_analysis': {
                    'core_competencies': {
                        'primary_skills': profile_analysis.get('skills', []),
                        'skill_frequency': profile_analysis.get('skill_frequencies', {})
                    },
                    'experience_level': {
                        'years': profile_analysis.get('minimum_experience', 0),
                        'roles': profile_analysis.get('roles', []),
                        'leadership_roles': profile_analysis.get('leadership_roles', [])
                    },
                    'technical_depth': {
                        'skills': profile_analysis.get('technical_skills', []),
                        'expertise_areas': profile_analysis.get('expertise_areas', [])
                    },
                    'leadership': {
                        'positions': profile_analysis.get('leadership_positions', []),
                        'team_size': profile_analysis.get('team_size', 0)
                    },
                    'industry_focus': {
                        'industries': profile_analysis.get('industries', []),
                        'domain_expertise': profile_analysis.get('domain_expertise', [])
                    },
                    'career_progression': {
                        'trajectory': profile_analysis.get('career_trajectory', ''),
                        'achievements': profile_analysis.get('achievements', [])
                    }
                }
            }

            filtered_jobs = []
            seen_jobs = set()
            
            for job in jobs:
                job_id = (job.get('title', ''), job.get('company', ''))
                if job_id in seen_jobs:
                    continue
                    
                job_with_match = self.calculate_profile_match(job, enhanced_profile)
                filtered_jobs.append(job_with_match)
                seen_jobs.add(job_id)
            
            return json.dumps(filtered_jobs)
            
        except Exception as e:
            print(f"Error processing jobs: {str(e)}")
            print(f"Profile Analysis Keys: {profile_analysis.keys() if profile_analysis else 'None'}")
            return json.dumps([])

    def calculate_profile_match(self, job: Dict[str, Any], profile_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate how well a job matches the profile using LLM"""
        try:
            # Safely extract ALL profile data with fallbacks
            core_comp = profile_analysis.get('core_competencies', {})
            exp_level = profile_analysis.get('experience_level', {})
            tech_depth = profile_analysis.get('technical_depth', {})
            leadership = profile_analysis.get('leadership_indicators', {})
            industry = profile_analysis.get('industry_focus', {})
            career = profile_analysis.get('career_progression', {})

            prompt = f"""
            As a job matching specialist, analyze the fit between the candidate's profile and the job requirements:

            Job Details:
            Title: {job.get('title', '')}
            Description: {job.get('description', '')}

            Candidate's Comprehensive Profile:
            1. Core Competencies:
               - Primary Skills: {core_comp.get('primary_skills', [])}
               - Skill Frequencies: {core_comp.get('skill_frequency', {})}

            2. Experience:
               - Seniority Level: {exp_level.get('seniority_level', 'Not specified')}
               - Leadership Roles: {exp_level.get('leadership_roles', [])}

            3. Technical Depth:
               - Core Technologies: {tech_depth.get('core_technologies', [])}
               - Technology Categories: {tech_depth.get('technology_categories', {})}
               - Expertise Level: {tech_depth.get('expertise_level', 'Not specified')}

            4. Leadership Experience:
               - Team Size Managed: {leadership.get('team_size_managed', 'Not specified')}
               - Leadership Positions: {leadership.get('leadership_roles', [])}
               - Key Achievements: {leadership.get('key_achievements', [])}

            5. Industry Focus:
               - Primary Industries: {industry.get('primary_industries', [])}
               - Specializations: {industry.get('specializations', [])}

            6. Career Progression:
               - Growth Trajectory: {career.get('growth_trajectory', 'Not specified')}
               - Career Path: {career.get('career_path', [])}

            Please provide:
            1. A match score (0-1) based on comprehensive profile alignment
            2. Detailed analysis of strengths and gaps
            3. Specific recommendations to improve profile match

            Return as JSON:
            {
                "match_score": <float 0-1>,
                "key_matches": [<matching skills/requirements>],
                "gaps": [<missing requirements>],
                "seniority_fit": <string assessment>,
                "leadership_fit": <string assessment>,
                "industry_alignment": <string assessment>,
                "career_trajectory_match": <string assessment>,
                "recommendations": [<specific suggestions>]
            }
            """

            if self.agent and hasattr(self.agent, 'llm'):
                analysis = self.agent.llm.invoke(prompt)
                try:
                    match_data = json.loads(analysis)
                    job_with_match = job.copy()
                    job_with_match.update({
                        'match_score': match_data.get('match_score', 0),
                        'match_analysis': match_data
                    })
                    return job_with_match
                except json.JSONDecodeError:
                    print("Warning: LLM response was not valid JSON")
                    
            # Fallback with basic matching if LLM fails
            job_with_match = job.copy()
            job_with_match['match_score'] = self._calculate_basic_match(job, profile_analysis)
            return job_with_match

        except Exception as e:
            print(f"Error in profile matching: {str(e)}")
            return {**job, 'match_score': 0}

    def meets_criteria(self, job: Dict[str, Any]) -> bool:
        """Check if job meets all criteria"""
        try:
            # Check minimum salary
            if self.min_salary:
                job_salary = job.get('minimum_salary', 0) or 0
                if job_salary < self.min_salary:
                    return False

            # Check contract type
            if self.contract_type:
                job_contract = (job.get('contract_type') or '').lower()
                if not job_contract or job_contract != self.contract_type.lower():
                    return False

            # Check keywords in title or description
            if self.keywords:
                text_to_search = (
                    f"{job.get('title', '')} {job.get('description', '')} "
                    f"{job.get('company', '')}"
                ).lower()
                
                if not any(keyword.lower() in text_to_search for keyword in self.keywords):
                    return False

            return True
            
        except Exception as e:
            print(f"Error processing job: {str(e)}")
            return False
