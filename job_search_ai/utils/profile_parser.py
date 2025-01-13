import re
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
from collections import Counter
from pathlib import Path
import traceback

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
        """Extract information from Medium HTML files"""
        if not self.medium_path:
            print("Debug: Medium path is not set")
            return None
        
        try:
            # Debug prints
            print(f"Debug: Medium path is {self.medium_path}")
            medium_path = Path(self.medium_path)
            print(f"Debug: Looking for HTML files in {medium_path}")
            
            # Check if directory exists
            if not medium_path.exists():
                print(f"Debug: Directory does not exist: {medium_path}")
                return None
            
            # List all HTML files found
            html_files = list(medium_path.glob('*.html'))
            print(f"Debug: Found {len(html_files)} HTML files")
            for file in html_files:
                print(f"Debug: Found file: {file}")
            
            articles = []
            
            # Process each HTML file
            for html_file in html_files:
                try:
                    with open(html_file, 'r', encoding='utf-8') as f:
                        print(f"Debug: Processing {html_file}")
                        soup = BeautifulSoup(f.read(), 'html.parser')
                        
                        # Extract article data
                        article = {
                            'title': soup.find('h1').text.strip() if soup.find('h1') else None,
                            'content': soup.get_text(separator=' ', strip=True),
                            'date': soup.find('time').text.strip() if soup.find('time') else None
                        }
                        
                        print(f"Debug: Extracted article: {article['title']}")
                        articles.append(article)
                except Exception as e:
                    print(f"Debug: Error processing file {html_file}: {str(e)}")
                    continue
            
            if not articles:
                print("Debug: No articles were successfully parsed")
                return None
            
            return {
                'articles': articles,
                'topics': self._normalize_list(self._extract_topics(' '.join([a['content'] for a in articles]))),
                'expertise': self._normalize_list(self._extract_expertise(' '.join([a['content'] for a in articles]))),
                'content_themes': self._extract_post_themes(' '.join([a['content'] for a in articles])),
                'article_count': len(articles)
            }
            
        except Exception as e:
            print(f"Error parsing Medium HTML files: {str(e)}")
            print(f"Debug: Exception type: {type(e)}")
            print(f"Debug: Exception traceback: {traceback.format_exc()}")
            return None

    def parse_linkedin_posts(self):
        """Extract information from LinkedIn posts PDF"""
        if not self.linkedin_posts_path:
            return None
        
        try:
            text = extract_text(self.linkedin_posts_path)
            
            return {
                'topics': self._normalize_list(self._extract_topics(text)),
                'expertise_areas': self._normalize_list(self._extract_expertise(text)),
                'key_themes': self._extract_post_themes(text),
                'engagement_metrics': self._extract_engagement_metrics(text),
                'content_summary': self._summarize_post_content(text)
            }
        except Exception as e:
            print(f"Error parsing LinkedIn posts: {str(e)}")
            return None

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

    def _extract_post_themes(self, text):
        """Extract main themes from posts"""
        themes = [
            'Digital Transformation', 'Cloud Computing', 'Leadership',
            'Technology Strategy', 'Innovation', 'AI/ML',
            'Project Management', 'Agile', 'Career Development'
        ]
        found_themes = []
        for theme in themes:
            if re.search(rf'\b{theme}\b', text, re.IGNORECASE):
                found_themes.append(theme)
        return self._normalize_list(found_themes)

    def _extract_engagement_metrics(self, text):
        """Extract engagement metrics from posts"""
        metrics = {
            'likes': self._extract_numbers(r'(\d+)\s*(?:likes?|reactions?)', text),
            'comments': self._extract_numbers(r'(\d+)\s*comments?', text),
            'shares': self._extract_numbers(r'(\d+)\s*shares?', text)
        }
        return metrics

    def _extract_numbers(self, pattern, text):
        """Extract numbers using regex pattern"""
        matches = re.findall(pattern, text, re.IGNORECASE)
        return [int(num) for num in matches if num.isdigit()]

    def _summarize_post_content(self, text):
        """Extract key points from post content"""
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        # Look for key content indicators
        key_points = []
        for para in paragraphs:
            # Look for bullet points or numbered lists
            if re.search(r'[•\-\d+\.]', para):
                key_points.append(para.strip())
            # Look for paragraphs with key phrases
            elif any(phrase in para.lower() for phrase in ['key takeaway', 'learned', 'insight', 'conclusion']):
                key_points.append(para.strip())
            
        return key_points[:5]  # Return top 5 key points
