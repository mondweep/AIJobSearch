from collections import Counter
import re
from pathlib import Path
import traceback

class ProfileAnalyzer:
    def __init__(self, profile_data):
        """
        profile_data contains parsed data from multiple sources:
        - cv: Basic CV data
        - cv_long: Detailed CV information
        - skills: LinkedIn skills
        - linkedin_posts: LinkedIn content/articles
        - linkedin_exp: LinkedIn experience
        - medium: Medium profile articles/expertise
        """
        self.profile_data = profile_data
        self.analysis = {}

    def analyze_profile(self):
        """Perform comprehensive profile analysis"""
        try:
            print("\nStarting profile analysis...")
            
            # Debug input data
            print(f"\nInput profile_data keys: {self.profile_data.keys()}")
            
            self.analysis = {}
            
            # Core competencies analysis
            print("\nAnalyzing core competencies...")
            self.analysis['core_competencies'] = self._analyze_core_competencies()
            print(f"Core competencies result: {self.analysis['core_competencies']}")
            
            # Experience level analysis
            print("\nAnalyzing experience level...")
            self.analysis['experience_level'] = self._analyze_experience_level()
            print(f"Experience level result: {self.analysis['experience_level']}")
            
            # Leadership analysis
            print("\nAnalyzing leadership indicators...")
            self.analysis['leadership_indicators'] = self._analyze_leadership()
            print(f"Leadership indicators result: {self.analysis['leadership_indicators']}")
            
            # Technical depth analysis
            print("\nAnalyzing technical depth...")
            self.analysis['technical_depth'] = self._analyze_technical_depth()
            print(f"Technical depth result: {self.analysis['technical_depth']}")
            
            # Industry focus analysis
            print("\nAnalyzing industry focus...")
            self.analysis['industry_focus'] = self._analyze_industry_focus()
            print(f"Industry focus result: {self.analysis['industry_focus']}")
            
            # Career progression analysis
            print("\nAnalyzing career progression...")
            self.analysis['career_progression'] = self._analyze_career_progression()
            print(f"Career progression result: {self.analysis['career_progression']}")
            
            # Skill gaps analysis
            print("\nAnalyzing skill gaps...")
            self.analysis['skill_gaps'] = self._identify_skill_gaps()
            print(f"Skill gaps result: {self.analysis['skill_gaps']}")
            
            print("\nProfile analysis completed successfully")
            return self.analysis
            
        except Exception as e:
            print(f"\nError in profile analysis: {str(e)}")
            print(f"Exception type: {type(e)}")
            print(f"Traceback:\n{traceback.format_exc()}")
            
            # Return partial analysis if available
            if hasattr(self, 'analysis') and self.analysis:
                print(f"\nReturning partial analysis: {list(self.analysis.keys())}")
                return self.analysis
            
            # Return empty analysis if nothing available
            print("\nReturning empty analysis due to error")
            return {
                'core_competencies': {'primary_skills': [], 'skill_frequency': {}},
                'experience_level': None,
                'leadership_indicators': {},
                'technical_depth': {},
                'industry_focus': {},
                'career_progression': {},
                'skill_gaps': {}
            }

    def _analyze_core_competencies(self):
        """Analyze main areas of expertise with safe handling of None values"""
        # Initialize empty list for all skills
        all_skills = []
        
        try:
            # Safely get data from each source with detailed error handling
            cv_data = self.profile_data.get('cv') or {}
            cv_long_data = self.profile_data.get('cv_long') or {}
            skills_data = self.profile_data.get('skills') or {}
            linkedin_data = self.profile_data.get('linkedin') or {}
            medium_data = self.profile_data.get('medium') or {}
            
            # CV data handling
            if isinstance(cv_data, dict):
                all_skills.extend(cv_data.get('skills', []))
                print(f"Debug: Added {len(cv_data.get('skills', []))} skills from CV")
            
            # Skills section handling
            if isinstance(skills_data, dict):
                technical_skills = skills_data.get('technical', [])
                soft_skills = skills_data.get('soft', [])
                all_skills.extend(technical_skills)
                all_skills.extend(soft_skills)
                print(f"Debug: Added {len(technical_skills)} technical and {len(soft_skills)} soft skills")
            
            # LinkedIn data handling
            if isinstance(linkedin_data, dict):
                # Experience skills
                linkedin_exp = linkedin_data.get('experience', {})
                exp_skills = linkedin_exp.get('skills', [])
                all_skills.extend(exp_skills)
                print(f"Debug: Added {len(exp_skills)} skills from LinkedIn experience")
                
                # Post topics and expertise
                linkedin_posts = linkedin_data.get('posts', {})
                post_topics = linkedin_posts.get('topics', [])
                post_expertise = linkedin_posts.get('expertise_areas', [])
                all_skills.extend(post_topics)
                all_skills.extend(post_expertise)
                print(f"Debug: Added {len(post_topics)} topics and {len(post_expertise)} expertise areas from LinkedIn posts")
            
            # Medium data handling
            if isinstance(medium_data, dict):
                medium_topics = medium_data.get('topics', [])
                medium_expertise = medium_data.get('expertise', [])
                all_skills.extend(medium_topics)
                all_skills.extend(medium_expertise)
                print(f"Debug: Added {len(medium_topics)} topics and {len(medium_expertise)} expertise areas from Medium")
            
            # Count skill frequencies with detailed logging
            skill_counter = Counter(all_skills)
            print(f"Debug: Total unique skills found: {len(skill_counter)}")
            
            return {
                'primary_skills': [skill for skill, count in skill_counter.most_common(10)],
                'skill_frequency': dict(skill_counter),
                'source_distribution': {
                    'cv': len(cv_data.get('skills', [])),
                    'technical_skills': len(skills_data.get('technical', [])),
                    'soft_skills': len(skills_data.get('soft', [])),
                    'linkedin': len(linkedin_exp.get('skills', [])) if isinstance(linkedin_data, dict) else 0,
                    'medium': len(medium_topics) + len(medium_expertise) if isinstance(medium_data, dict) else 0
                }
            }
            
        except Exception as e:
            print(f"Error in core competencies analysis: {str(e)}")
            print(f"Debug: Exception type: {type(e)}")
            print(f"Debug: Exception traceback: {traceback.format_exc()}")
            return {
                'primary_skills': [],
                'skill_frequency': {},
                'source_distribution': {}
            }

    def _analyze_experience_level(self):
        """Enhanced experience analysis using multiple sources"""
        linkedin_data = self.profile_data.get('linkedin_exp', {})
        cv_data = self.profile_data.get('cv', {})
        cv_long_data = self.profile_data.get('cv_long', {})
        
        # Combine roles from all sources
        all_roles = []
        all_roles.extend(linkedin_data.get('roles', []))
        all_roles.extend(cv_data.get('experiences', []))
        all_roles.extend(cv_long_data.get('experiences', []))
        
        # Identify leadership roles
        leadership_roles = [
            role for role in all_roles 
            if any(title in role.lower() for title in 
                ['head', 'director', 'lead', 'manager', 'chief'])
        ]
        
        return {
            'leadership_roles': leadership_roles,
            'total_roles': len(set(all_roles)),
            'seniority_level': self._determine_seniority(all_roles),
            'companies': linkedin_data.get('companies', [])
        }

    def _analyze_content_expertise(self):
        """New method to analyze thought leadership content"""
        linkedin_posts = self.profile_data.get('linkedin_posts', {})
        medium_data = self.profile_data.get('medium', {})
        
        return {
            'linkedin_topics': linkedin_posts.get('topics', []),
            'medium_expertise': medium_data.get('expertise', []),
            'thought_leadership_areas': list(set(
                linkedin_posts.get('topics', []) + 
                medium_data.get('expertise', [])
            ))
        }

    def _analyze_leadership(self):
        """Analyze leadership experience and capabilities"""
        cv_data = self.profile_data.get('cv', {})
        linkedin_data = self.profile_data.get('linkedin', {})
        
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
        skills_data = self.profile_data.get('skills', {})
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
        linkedin_data = self.profile_data.get('linkedin', {})
        cv_data = self.profile_data.get('cv', {})
        
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
        linkedin_data = self.profile_data.get('linkedin', {})
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
