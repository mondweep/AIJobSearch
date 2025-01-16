from collections import Counter
import re
from pathlib import Path
import traceback
from typing import Dict, Any, Set, List, Tuple
from itertools import chain

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
        self.profile_data = profile_data or {}
        self.analysis = {}

    def _safe_get(self, data, *keys, default=None):
        """Safely get nested dictionary values"""
        current = data
        for key in keys:
            if not isinstance(current, dict):
                return default
            current = current.get(key, default)
            if current is None:
                return default
        return current

    def analyze_profile(self):
        """Analyze the complete profile data"""
        analysis = {
            'core_competencies': self._analyze_core_competencies(),
            'experience_level': self._analyze_experience_level(),
            'technical_depth': self._analyze_technical_depth(),
            'leadership': self._analyze_leadership(),
            'education': self._analyze_education(),  # New
            'certifications': self._analyze_certifications(),  # New
            'endorsements': self._analyze_endorsements(),  # New
            'content_expertise': self._analyze_content_expertise(),
            'industry_focus': self._analyze_industry_focus(),
            'career_progression': self._analyze_career_progression()
        }
        return analysis

    def _analyze_core_competencies(self):
        """Analyze core competencies with enhanced skill categorization"""
        try:
            # Get skills from all sources
            cv_skills = set(self._safe_get(self.profile_data, 'cv', 'skills', default=[]))
            linkedin_skills = set(self._extract_linkedin_skills(self._safe_get(self.profile_data, 'linkedin', default={})))
            technical_skills = set(self._safe_get(self.profile_data, 'skills', 'technical', default=[]))
            soft_skills = set(self._safe_get(self.profile_data, 'skills', 'soft', default=[]))
            
            # Combine all skills
            all_skills = cv_skills | linkedin_skills | technical_skills | soft_skills
            
            # Count skill frequencies
            skill_counter = Counter(all_skills)
            
            # Get topics from content
            linkedin_topics = set(self._safe_get(self.profile_data, 'linkedin_posts', 'topics', default=[]))
            medium_topics = set(self._extract_medium_topics(self._safe_get(self.profile_data, 'medium', default={})))
            
            print(f"Debug: Found {len(cv_skills)} CV skills")
            print(f"Debug: Found {len(technical_skills)} technical skills")
            print(f"Debug: Found {len(soft_skills)} soft skills")
            print(f"Debug: Found {len(linkedin_topics)} LinkedIn topics")
            print(f"Debug: Found {len(medium_topics)} Medium topics")
            
            return {
                'primary_skills': [skill for skill, count in skill_counter.most_common(10)],
                'skill_frequency': dict(skill_counter),
                'source_distribution': {
                    'cv': len(cv_skills),
                    'technical_skills': len(technical_skills),
                    'soft_skills': len(soft_skills),
                    'linkedin_topics': len(linkedin_topics),
                    'medium_topics': len(medium_topics)
                }
            }
            
        except Exception as e:
            print(f"Error in core competencies analysis: {str(e)}")
            traceback.print_exc()
            return {
                'primary_skills': [],
                'skill_frequency': {},
                'source_distribution': {}
            }

    def _analyze_experience_level(self):
        """Enhanced experience analysis using multiple sources"""
        linkedin_data = self._safe_get(self.profile_data, 'linkedin_exp', default={})
        cv_data = self._safe_get(self.profile_data, 'cv', default={})
        cv_long_data = self._safe_get(self.profile_data, 'cv_long', default={})
        
        # Combine roles from all sources
        all_roles = []
        all_roles.extend(self._safe_get(linkedin_data, 'roles', default=[]))
        all_roles.extend(self._safe_get(cv_data, 'experiences', default=[]))
        all_roles.extend(self._safe_get(cv_long_data, 'experiences', default=[]))
        
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
            'companies': self._safe_get(linkedin_data, 'companies', default=[])
        }

    def _analyze_content_expertise(self):
        """Analyze thought leadership content from both posts and articles"""
        linkedin_posts = self._safe_get(self.profile_data, 'linkedin_posts', default={})
        linkedin_articles = self._safe_get(self.profile_data, 'linkedin_articles', default={})
        medium_data = self._safe_get(self.profile_data, 'medium', default={})
        
        # Combine topics from all sources
        all_topics = set()
        all_topics.update(self._safe_get(linkedin_posts, 'topics', default=[]))
        all_topics.update(self._safe_get(linkedin_articles, 'topics', default=[]))
        all_topics.update(self._safe_get(medium_data, 'topics', default=[]))
        
        return {
            'linkedin_post_topics': self._safe_get(linkedin_posts, 'topics', default=[]),
            'linkedin_article_topics': self._safe_get(linkedin_articles, 'topics', default=[]),
            'medium_expertise': self._safe_get(medium_data, 'expertise', default=[]),
            'thought_leadership_areas': list(all_topics)
        }

    def _analyze_leadership(self):
        """Analyze leadership experience and capabilities"""
        cv_data = self._safe_get(self.profile_data, 'cv', default={})
        linkedin_data = self._safe_get(self.profile_data, 'linkedin', default={})
        
        leadership_indicators = {
            'team_size_managed': self._extract_team_size(cv_data),
            'leadership_roles': [],
            'key_achievements': self._extract_achievements(cv_data)
        }
        
        roles = self._safe_get(linkedin_data, 'roles', default=[])
        if roles:
            leadership_indicators['leadership_roles'] = [
                role for role in roles
                if any(title in role.lower() for title in 
                    ['head', 'director', 'lead', 'manager', 'chief'])
            ]
        
        return leadership_indicators

    def _analyze_technical_depth(self):
        """Analyze technical expertise level"""
        skills_data = self._safe_get(self.profile_data, 'skills', default={})
        if not skills_data:
            return {}
        
        technical_skills = self._safe_get(skills_data, 'technical', default=[])
        
        return {
            'core_technologies': technical_skills[:5],
            'technology_categories': self._categorize_technologies(technical_skills),
            'expertise_level': self._determine_expertise_level(technical_skills)
        }

    def _analyze_industry_focus(self):
        """Analyze industry experience and focus areas"""
        linkedin_data = self._safe_get(self.profile_data, 'linkedin', default={})
        cv_data = self._safe_get(self.profile_data, 'cv', default={})
        
        industries = set()
        if linkedin_data and 'companies' in linkedin_data:
            for company in self._safe_get(linkedin_data, 'companies', default=[]):
                industries.update(self._extract_industries(company))
        
        return {
            'primary_industries': list(industries),
            'specializations': self._extract_specializations(cv_data)
        }

    def _analyze_career_progression(self):
        """Analyze career growth and progression"""
        linkedin_data = self._safe_get(self.profile_data, 'linkedin', default={})
        if not linkedin_data:
            return {}
        
        roles = self._safe_get(linkedin_data, 'roles', default=[])
        progression = {
            'career_path': self._analyze_role_progression(roles),
            'role_duration': self._analyze_role_durations(roles),
            'growth_trajectory': self._determine_growth_trajectory(roles)
        }
        
        return progression

    def _analyze_skill_gaps(self):
        """Analyze skill gaps based on profile data"""
        try:
            # Get all skills from different sources
            skills_from_cv = self._extract_skills_from_cv(self._safe_get(self.profile_data, 'cv', default={}))
            technical_skills = self._extract_technical_skills(self.profile_data)
            soft_skills = self._extract_soft_skills(self.profile_data)
            linkedin_skills = self._extract_linkedin_skills(self._safe_get(self.profile_data, 'linkedin', default={}))
            medium_skills = self._extract_medium_topics(self._safe_get(self.profile_data, 'medium', default={}))
            
            # Debug logging
            print(f"Debug: Added {len(skills_from_cv)} skills from CV")
            print(f"Debug: Added {len(technical_skills)} technical and {len(soft_skills)} soft skills")
            print(f"Debug: Added {len(linkedin_skills)} skills from LinkedIn experience")
            print(f"Debug: Added {len(medium_skills)} topics from Medium")
            
            # Combine all skills
            all_skills = set(chain(skills_from_cv, technical_skills, soft_skills, linkedin_skills, medium_skills))
            print(f"Debug: Total unique skills found: {len(all_skills)}")
            
            # Compare against required skills for target roles
            missing_skills = self._identify_missing_skills(all_skills)
            development_areas = self._identify_development_areas(all_skills)
            
            return {
                'missing_skills': list(missing_skills),
                'development_areas': list(development_areas)
            }
        except Exception as e:
            print(f"Error in skill gaps analysis: {str(e)}")
            print(f"Debug: Exception type: {type(e)}")
            print(f"Debug: Exception traceback: {traceback.format_exc()}")
            return {
                'missing_skills': [],
                'development_areas': []
            }

    def _analyze_education(self):
        """Analyze education background"""
        education_data = self._safe_get(self.profile_data, 'linkedin', 'education', default=[])
        if not education_data:
            return {
                'degrees': [],
                'institutions': [],
                'fields_of_study': []
            }
            
        return {
            'degrees': [self._safe_get(edu, 'degree', default='') for edu in education_data],
            'institutions': [self._safe_get(edu, 'school', default='') for edu in education_data],
            'fields_of_study': [self._safe_get(edu, 'field_of_study', default='') for edu in education_data]
        }

    def _analyze_certifications(self):
        """Analyze professional certifications"""
        cert_data = self._safe_get(self.profile_data, 'linkedin', 'certifications', 'certifications', default=[])
        if not cert_data:
            return {
                'certifications': [],
                'authorities': [],
                'total_count': 0
            }
        
        # Extract unique certification names and authorities
        certifications = []
        for cert in cert_data:
            cert_info = {
                'name': self._safe_get(cert, 'name', default=''),
                'authority': self._safe_get(cert, 'authority', default=''),
                'date': self._safe_get(cert, 'date', default='')
            }
            if cert_info['name']:  # Only add if name exists
                certifications.append(cert_info)
        
        # Get unique authorities
        authorities = list(set(cert['authority'] for cert in certifications if cert['authority']))
        
        return {
            'certifications': certifications,
            'authorities': authorities,
            'total_count': len(certifications)
        }

    def _analyze_endorsements(self):
        """Analyze LinkedIn endorsements"""
        endorsements = self._safe_get(self.profile_data, 'linkedin', 'endorsements', default={})
        if not endorsements:
            return {
                'top_skills': [],
                'total_endorsements': 0,
                'skill_categories': {}
            }
        
        try:
            # Sort endorsements by count
            sorted_skills = sorted(
                endorsements.items(),
                key=lambda x: int(x[1]) if isinstance(x[1], (int, str)) else 0,
                reverse=True
            )
            
            # Get top skills (top 10)
            top_skills = [(skill, count) for skill, count in sorted_skills[:10]]
            
            # Categorize skills
            skill_categories = {
                'technical': [],
                'soft': [],
                'industry': [],
                'other': []
            }
            
            for skill, count in sorted_skills:
                category = self._categorize_skill(skill)
                skill_categories[category].append((skill, count))
            
            return {
                'top_skills': top_skills,
                'total_endorsements': sum(int(count) if isinstance(count, (int, str)) else 0 
                                       for _, count in sorted_skills),
                'skill_categories': skill_categories
            }
            
        except Exception as e:
            print(f"Error analyzing endorsements: {str(e)}")
            return {
                'top_skills': [],
                'total_endorsements': 0,
                'skill_categories': {}
            }

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

    def _extract_skills_from_cv(self, text: str) -> List[str]:
        """Extract skills from text using predefined patterns"""
        # Technical skills patterns
        technical_patterns = [
            r'\b(Python|Java|AWS|Azure|GCP|Cloud|AI|ML|DevOps|Kubernetes|Docker)\b',
            r'\b(Agile|Scrum|Kanban|JIRA|Confluence)\b',
            r'\b(SQL|NoSQL|MongoDB|PostgreSQL|MySQL)\b',
            r'\b(CI/CD|Jenkins|Git|GitHub|BitBucket)\b',
            r'\b(REST|API|Microservices|Architecture)\b'
        ]
        
        # Soft skills patterns
        soft_patterns = [
            r'\b(Leadership|Management|Strategy|Vision)\b',
            r'\b(Communication|Presentation|Negotiation)\b',
            r'\b(Problem[-\s]Solving|Decision[-\s]Making)\b',
            r'\b(Team[-\s]Building|Mentoring|Coaching)\b',
            r'\b(Project[-\s]Management|Program[-\s]Management)\b'
        ]
        
        skills = set()
        
        # Extract skills using patterns
        for pattern in technical_patterns + soft_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            skills.update([match.strip() for match in matches if match.strip()])
        
        return list(skills)

    def _extract_technical_skills(self, profile_data):
        """Extract technical skills from profile data"""
        skills_data = self._safe_get(profile_data, 'skills', default={})
        if not skills_data:
            return []
        
        return self._safe_get(skills_data, 'technical', default=[])

    def _extract_soft_skills(self, profile_data):
        """Extract soft skills from profile data"""
        skills_data = self._safe_get(profile_data, 'skills', default={})
        if not skills_data:
            return []
        
        return self._safe_get(skills_data, 'soft', default=[])

    def _extract_linkedin_skills(self, linkedin_data: Dict[str, Any]) -> List[str]:
        """Extract skills from LinkedIn experience descriptions"""
        skills = set()
        for exp in self._safe_get(linkedin_data, 'experiences', default=[]):
            description = exp.get('description', '')
            role = exp.get('title', '')
            # Use _extract_skills_from_cv instead of non-existent _extract_skills_from_text
            extracted_skills = self._extract_skills_from_cv(description + ' ' + role)
            if extracted_skills:
                skills.update(extracted_skills)
        return list(skills)

    def _extract_medium_topics(self, medium_data):
        """Extract topics from Medium data"""
        if not medium_data:
            return []
        
        topics = []
        if isinstance(medium_data, dict):
            topics.extend(self._safe_get(medium_data, 'topics', default=[]))
        
        return topics

    def _identify_missing_skills(self, current_skills):
        """Identify missing skills based on job market requirements"""
        # Use frequency analysis to avoid marking skills as "missing" if they appear in profile
        skill_frequency = self._calculate_skill_frequency(current_skills)
        
        # Consider skill variations (e.g., "Project Management" vs "PM")
        normalized_skills = self._normalize_skills(current_skills)
        
        # Compare against market requirements
        required_skills = self._get_market_required_skills()
        truly_missing = set()
        
        for skill in required_skills:
            normalized_skill = self._normalize_skill(skill)
            if normalized_skill not in normalized_skills and skill_frequency.get(skill, 0) == 0:
                truly_missing.add(skill)
        
        return truly_missing

    def _normalize_skill(self, skill):
        """Normalize skill names for better matching"""
        # Convert to lowercase
        normalized = skill.lower()
        
        # Handle common variations
        variations = {
            'project management': ['pm', 'project manager', 'program management'],
            'python': ['py', 'python programming'],
            'aws': ['amazon web services', 'amazon aws'],
            # Add more variations as needed
        }
        
        # Check if skill is a known variation
        for standard, variants in variations.items():
            if normalized in variants:
                return standard
            
        return normalized

    def _calculate_skill_frequency(self, skills):
        """Calculate skill frequency"""
        skill_counter = Counter(skills)
        return dict(skill_counter)

    def _normalize_skills(self, skills):
        """Normalize skills"""
        # This method is not implemented in the code block, so it's left unchanged
        pass

    def _get_market_required_skills(self):
        """Get market required skills"""
        # This method is not implemented in the code block, so it's left unchanged
        pass

    def _calculate_match_score(self, job: Dict[str, Any], profile: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate detailed match score between job and profile"""
        try:
            print("\n=== Match Score Calculation ===")
            
            # Get profile components
            skills = profile.get('analysis', {}).get('core_competencies', {})
            experience = profile.get('analysis', {}).get('experience_level', {})
            leadership = profile.get('analysis', {}).get('leadership', {})
            endorsements = profile.get('analysis', {}).get('endorsements', {})
            
            print(f"Skills found: {len(skills.get('primary_skills', []))}")
            print(f"Experience data: {bool(experience)}")
            print(f"Leadership indicators: {bool(leadership)}")
            print(f"Endorsements: {len(endorsements)}")
            
            # Calculate component scores
            skill_score = self._calculate_skill_match(job, skills)
            exp_score = self._calculate_experience_match(job, experience)
            leadership_score = self._calculate_leadership_match(job, leadership)
            endorsement_score = self._calculate_endorsement_match(job, endorsements)
            
            print("\n=== Component Scores ===")
            print(f"Skill Match: {skill_score:.2f}")
            print(f"Experience Match: {exp_score:.2f}")
            print(f"Leadership Match: {leadership_score:.2f}")
            print(f"Endorsement Match: {endorsement_score:.2f}")
            
            # Calculate weighted total
            total_score = (
                skill_score * 0.4 +
                exp_score * 0.3 +
                leadership_score * 0.2 +
                endorsement_score * 0.1
            )
            
            return {
                'score': round(total_score, 2),
                'components': {
                    'skills': round(skill_score, 2),
                    'experience': round(exp_score, 2),
                    'leadership': round(leadership_score, 2),
                    'endorsements': round(endorsement_score, 2)
                },
                'matched_skills': self._get_matching_skills(job, skills)
            }
            
        except Exception as e:
            print(f"Error calculating match score: {str(e)}")
            traceback.print_exc()
            return {'score': 0.0, 'error': str(e)}

    def generate_profile_summary(self) -> Dict[str, Any]:
        """Generate a structured summary of the profile for LLM analysis"""
        try:
            summary = {
                'technical_expertise': {
                    'primary_skills': self._analyze_technical_depth().get('core_technologies', []),
                    'certifications': self._analyze_certifications().get('certifications', []),
                    'technical_projects': self._extract_technical_projects()
                },
                'leadership_experience': {
                    'roles': self._analyze_leadership().get('leadership_roles', []),
                    'team_size': self._analyze_leadership().get('team_size_managed', 'Unknown'),
                    'key_achievements': self._analyze_leadership().get('key_achievements', [])
                },
                'industry_knowledge': {
                    'primary_industries': self._analyze_industry_focus().get('primary_industries', []),
                    'specializations': self._analyze_industry_focus().get('specializations', [])
                },
                'career_progression': {
                    'experience_level': self._analyze_experience_level().get('seniority_level', ''),
                    'total_years': self._calculate_total_experience(),
                    'career_highlights': self._extract_career_highlights()
                }
            }
            return summary
        except Exception as e:
            print(f"Error generating profile summary: {str(e)}")
            return {}
