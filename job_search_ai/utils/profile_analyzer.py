from collections import Counter
import re
from pathlib import Path

class ProfileAnalyzer:
    def __init__(self, profile_parser):
        self.parser = profile_parser
        self.analysis = {}

    def analyze_profile(self):
        """Perform comprehensive profile analysis"""
        self.analysis = {
            'core_competencies': self._analyze_core_competencies(),
            'experience_level': self._analyze_experience_level(),
            'leadership_indicators': self._analyze_leadership(),
            'technical_depth': self._analyze_technical_depth(),
            'industry_focus': self._analyze_industry_focus(),
            'career_progression': self._analyze_career_progression(),
            'skill_gaps': self._identify_skill_gaps()
        }
        return self.analysis

    def _analyze_core_competencies(self):
        """Analyze main areas of expertise"""
        skills_data = self.parser.parse_skills()
        cv_data = self.parser.parse_cv()
        
        all_skills = []
        if skills_data:
            all_skills.extend(skills_data.get('technical', []))
            all_skills.extend(skills_data.get('soft', []))
        if cv_data:
            all_skills.extend(cv_data.get('skills', []))
        
        # Count skill frequencies
        skill_counter = Counter(all_skills)
        
        return {
            'primary_skills': [skill for skill, count in skill_counter.most_common(5)],
            'skill_frequency': dict(skill_counter)
        }

    def _analyze_experience_level(self):
        """Analyze years of experience and seniority"""
        linkedin_data = self.parser.parse_linkedin_experience()
        if not linkedin_data:
            return {}
        
        roles = linkedin_data.get('roles', [])
        leadership_roles = sum(1 for role in roles if any(
            title in role.lower() for title in 
            ['head', 'director', 'lead', 'manager', 'chief']
        ))
        
        return {
            'leadership_roles': leadership_roles,
            'total_roles': len(roles),
            'seniority_level': self._determine_seniority(roles)
        }

    def _analyze_leadership(self):
        """Analyze leadership experience and capabilities"""
        cv_data = self.parser.parse_cv()
        linkedin_data = self.parser.parse_linkedin_experience()
        
        leadership_indicators = {
            'team_size_managed': self._extract_team_size(cv_data),
            'leadership_roles': [],
            'key_achievements': self._extract_achievements(cv_data)
        }
        
        if linkedin_data and 'roles' in linkedin_data:
            leadership_indicators['leadership_roles'] = [
                role for role in linkedin_data['roles']
                if any(title in role.lower() for title in 
                    ['head', 'director', 'lead', 'manager', 'chief'])
            ]
        
        return leadership_indicators

    def _analyze_technical_depth(self):
        """Analyze technical expertise level"""
        skills_data = self.parser.parse_skills()
        if not skills_data:
            return {}
        
        technical_skills = skills_data.get('technical', [])
        
        return {
            'core_technologies': technical_skills[:5],
            'technology_categories': self._categorize_technologies(technical_skills),
            'expertise_level': self._determine_expertise_level(technical_skills)
        }

    def _analyze_industry_focus(self):
        """Analyze industry experience and focus areas"""
        linkedin_data = self.parser.parse_linkedin_experience()
        cv_data = self.parser.parse_cv()
        
        industries = set()
        if linkedin_data and 'companies' in linkedin_data:
            for company in linkedin_data['companies']:
                industries.update(self._extract_industries(company))
        
        return {
            'primary_industries': list(industries),
            'specializations': self._extract_specializations(cv_data)
        }

    def _analyze_career_progression(self):
        """Analyze career growth and progression"""
        linkedin_data = self.parser.parse_linkedin_experience()
        if not linkedin_data:
            return {}
        
        roles = linkedin_data.get('roles', [])
        progression = {
            'career_path': self._analyze_role_progression(roles),
            'role_duration': self._analyze_role_durations(roles),
            'growth_trajectory': self._determine_growth_trajectory(roles)
        }
        
        return progression

    def _identify_skill_gaps(self):
        """Identify potential skill gaps based on target roles"""
        current_skills = set(self._analyze_core_competencies()['primary_skills'])
        target_skills = self._get_target_role_skills()
        
        return {
            'missing_skills': list(target_skills - current_skills),
            'development_areas': self._identify_development_areas(current_skills)
        }

    # Helper methods
    def _determine_seniority(self, roles):
        """Determine seniority level based on roles"""
        leadership_keywords = ['head', 'director', 'lead', 'manager', 'chief', 'principal']
        senior_count = sum(1 for role in roles if any(keyword in role.lower() for keyword in leadership_keywords))
        
        if senior_count >= 2:
            return "Senior"
        elif senior_count >= 1:
            return "Mid-Senior"
        else:
            return "Mid-Level"

    def _extract_team_size(self, cv_data):
        """Extract team size from CV data"""
        if not cv_data:
            return "Unknown"
        
        text = str(cv_data.get('experiences', ''))
        team_sizes = re.findall(r'team of (\d+)', text, re.IGNORECASE)
        if team_sizes:
            return max(map(int, team_sizes))
        return "Not specified"

    def _extract_achievements(self, cv_data):
        """Extract key achievements from CV data"""
        if not cv_data:
            return []
        
        text = str(cv_data.get('experiences', ''))
        achievements = []
        achievement_keywords = ['achieved', 'delivered', 'improved', 'increased', 'reduced', 'implemented']
        
        for line in text.split('\n'):
            if any(keyword in line.lower() for keyword in achievement_keywords):
                achievements.append(line.strip())
        
        return achievements[:5]  # Return top 5 achievements

    def _categorize_technologies(self, skills):
        """Categorize technical skills"""
        categories = {
            'Cloud': ['aws', 'azure', 'gcp', 'cloud'],
            'Programming': ['python', 'java', 'javascript', 'c++'],
            'Data': ['sql', 'mongodb', 'elasticsearch'],
            'DevOps': ['kubernetes', 'docker', 'jenkins'],
            'AI/ML': ['ai', 'ml', 'tensorflow', 'pytorch']
        }
        
        categorized = {}
        for category, keywords in categories.items():
            matching_skills = [skill for skill in skills if any(keyword in skill.lower() for keyword in keywords)]
            if matching_skills:
                categorized[category] = matching_skills
        
        return categorized

    def _determine_expertise_level(self, skills):
        """Determine expertise level based on skills"""
        expertise_levels = {
            'Expert': ['architect', 'lead', 'senior', 'principal'],
            'Advanced': ['developer', 'engineer', 'analyst'],
            'Intermediate': ['associate', 'junior']
        }
        
        for level, keywords in expertise_levels.items():
            if any(keyword in ' '.join(skills).lower() for keyword in keywords):
                return level
        return "Intermediate"

    def _extract_industries(self, company):
        """Extract industries from company information"""
        industry_keywords = {
            'Technology': ['tech', 'software', 'it'],
            'Finance': ['bank', 'finance', 'investment'],
            'Healthcare': ['health', 'medical', 'pharma'],
            'Consulting': ['consult', 'advisory'],
            'Manufacturing': ['manufacturing', 'production']
        }
        
        industries = set()
        company_lower = company.lower()
        
        for industry, keywords in industry_keywords.items():
            if any(keyword in company_lower for keyword in keywords):
                industries.add(industry)
        
        return industries

    def _extract_specializations(self, cv_data):
        """Extract specializations from CV data"""
        if not cv_data:
            return []
        
        specialization_keywords = [
            'specialist in', 'specialized in', 'focus on',
            'expertise in', 'experienced in'
        ]
        
        text = str(cv_data.get('experiences', ''))
        specializations = []
        
        for keyword in specialization_keywords:
            matches = re.findall(f"{keyword} (.*?)(?:[.]|$)", text, re.IGNORECASE)
            specializations.extend(matches)
        
        return list(set(specializations))

    def _analyze_role_progression(self, roles):
        """Analyze career progression through roles"""
        progression = []
        for role in roles:
            level = "Senior" if any(word in role.lower() for word in ['senior', 'lead', 'head', 'director']) else "Regular"
            progression.append({'role': role, 'level': level})
        return progression

    def _analyze_role_durations(self, roles):
        """Analyze duration in roles"""
        return len(roles)  # Simplified version

    def _determine_growth_trajectory(self, roles):
        """Determine career growth trajectory"""
        leadership_roles = sum(1 for role in roles if any(
            word in role.lower() for word in ['senior', 'lead', 'head', 'director']
        ))
        
        if leadership_roles >= 2:
            return "Leadership Track"
        elif leadership_roles >= 1:
            return "Management Track"
        else:
            return "Technical Track"

    def _get_target_role_skills(self):
        """Get required skills for target roles"""
        # Define common skills for senior technical roles
        target_skills = {
            'Python',
            'Cloud',
            'AWS',
            'Azure',
            'Leadership',
            'Project Management',
            'Architecture',
            'Strategy'
        }
        return target_skills

    def _identify_development_areas(self, current_skills):
        """Identify areas for skill development"""
        core_areas = {
            'Technical': ['cloud', 'aws', 'azure', 'python'],
            'Leadership': ['management', 'leadership', 'strategy'],
            'Domain': ['architecture', 'security', 'agile']
        }
        
        development_areas = []
        current_skills_lower = {skill.lower() for skill in current_skills}
        
        for area, required_skills in core_areas.items():
            if not any(skill in current_skills_lower for skill in required_skills):
                development_areas.append(area)
        
        return development_areas
