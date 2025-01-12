import re
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
from collections import Counter

class ProfileParser:
    def __init__(self, cv_path=None, cv_long_path=None, cv_more_path=None,
                 skills_path=None, linkedin_posts_path=None, 
                 linkedin_exp_path=None, medium_path=None):
        self.cv_path = cv_path
        self.cv_long_path = cv_long_path
        self.cv_more_path = cv_more_path
        self.skills_path = skills_path
        self.linkedin_posts_path = linkedin_posts_path
        self.linkedin_exp_path = linkedin_exp_path
        self.medium_path = medium_path

    def _normalize_list(self, items):
        """Normalize list items to remove duplicates and standardize case"""
        # Convert all items to title case and remove duplicates
        normalized = {item.title() for item in items if item}
        return sorted(list(normalized))

    def parse_cv(self):
        """Extract text from CV PDF and analyze for skills and experiences"""
        if not self.cv_path:
            return None
        
        text = extract_text(self.cv_path)
        analysis = self._analyze_text(text)
        
        return {
            'skills': self._normalize_list(analysis['skills']),
            'experiences': self._normalize_list(analysis['experiences'])
        }

    def parse_skills(self):
        """Extract skills from LinkedIn Skills PDF"""
        if not self.skills_path:
            return None
        
        text = extract_text(self.skills_path)
        return {
            'technical': self._normalize_list(self._extract_technical_skills(text)),
            'soft': self._normalize_list(self._extract_soft_skills(text))
        }

    def parse_linkedin_experience(self):
        """Extract experience from LinkedIn Experience PDF"""
        if not self.linkedin_exp_path:
            return None
        
        text = extract_text(self.linkedin_exp_path)
        return {
            'roles': self._normalize_list(self._extract_roles(text)),
            'companies': self._normalize_list(self._extract_companies(text))
        }

    def parse_medium_profile(self):
        """Extract information from Medium Profile PDF"""
        if not self.medium_path:
            return None
        
        text = extract_text(self.medium_path)
        return {
            'topics': self._normalize_list(self._extract_topics(text)),
            'expertise': self._normalize_list(self._extract_expertise(text))
        }

    def _analyze_text(self, text):
        """Analyze text to extract skills and experiences"""
        technical_skills = [
            'Python', 'Java', 'AWS', 'Azure', 'Cloud', 'AI', 'ML', 
            'DevOps', 'Agile', 'Project Management'
        ]
        
        roles = [
            'Program Manager', 'Director', 'Engineer', 'Head', 'Lead',
            'Architect', 'CTO', 'Technical Program Manager'
        ]
        
        skills_pattern = '|'.join(technical_skills)
        roles_pattern = '|'.join(roles)
        
        skills = re.findall(f'\\b({skills_pattern})\\b', text, re.IGNORECASE)
        experiences = re.findall(f'\\b({roles_pattern})\\b', text, re.IGNORECASE)
        
        return {
            'skills': skills,
            'experiences': experiences
        }

    def _extract_technical_skills(self, text):
        """Extract technical skills from text"""
        skills = [
            'Python', 'Java', 'AWS', 'Azure', 'Cloud', 'AI', 'ML',
            'DevOps', 'Agile', 'Kubernetes', 'Docker', 'Microservices'
        ]
        pattern = '|'.join(skills)
        return re.findall(f'\\b({pattern})\\b', text, re.IGNORECASE)

    def _extract_soft_skills(self, text):
        """Extract soft skills from text"""
        skills = [
            'Leadership', 'Management', 'Communication', 'Strategy',
            'Vision', 'Innovation', 'Problem Solving', 'Team Building'
        ]
        pattern = '|'.join(skills)
        return re.findall(f'\\b({pattern})\\b', text, re.IGNORECASE)

    def _extract_roles(self, text):
        """Extract roles from text"""
        roles = [
            'Director', 'Manager', 'Lead', 'Head', 'Architect',
            'CTO', 'Technical Program Manager', 'Program Director'
        ]
        pattern = '|'.join(roles)
        return re.findall(f'\\b({pattern})\\b', text, re.IGNORECASE)

    def _extract_companies(self, text):
        """Extract company names from text"""
        companies = re.findall(r'(?:at|with)\s+([A-Z][A-Za-z\s]+(?:Inc\.|Ltd\.|LLC|Limited))', 
                             text)
        return list(set(companies))

    def _extract_topics(self, text):
        """Extract article topics"""
        topics = [
            'AI', 'ML', 'Cloud', 'Technology', 'Leadership',
            'Innovation', 'Digital Transformation', 'Strategy'
        ]
        pattern = '|'.join(topics)
        return re.findall(f'\\b({pattern})\\b', text, re.IGNORECASE)

    def _extract_expertise(self, text):
        """Extract areas of expertise"""
        areas = [
            'Technology', 'Strategy', 'Architecture', 'Management',
            'Digital Transformation', 'Innovation', 'Leadership'
        ]
        pattern = '|'.join(areas)
        return re.findall(f'\\b({pattern})\\b', text, re.IGNORECASE)
