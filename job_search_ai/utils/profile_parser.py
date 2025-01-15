import re
from pdfminer.high_level import extract_text
from bs4 import BeautifulSoup
from collections import Counter
from pathlib import Path
import traceback
import csv
import json
from langchain_openai import OpenAI
from typing import Dict, Any
import pandas as pd
import os

class ProfileParser:
    def __init__(self, cv_path=None, cv_long_path=None, cv_more_path=None,
                 skills_path=None, linkedin_posts_path=None, 
                 linkedin_exp_path=None, linkedin_positions_path=None,
                 linkedin_profile_path=None, linkedin_certifications_path=None,
                 linkedin_education_path=None, linkedin_endorsements_path=None,
                 linkedin_articles_path=None, medium_path=None):
        self.cv_path = cv_path
        self.cv_long_path = cv_long_path
        self.cv_more_path = cv_more_path
        self.skills_path = skills_path
        self.linkedin_posts_path = linkedin_posts_path
        self.linkedin_exp_path = linkedin_exp_path
        self.linkedin_positions_path = linkedin_positions_path
        self.linkedin_profile_path = linkedin_profile_path
        self.linkedin_certifications_path = linkedin_certifications_path
        self.linkedin_education_path = linkedin_education_path
        self.linkedin_endorsements_path = linkedin_endorsements_path
        self.linkedin_articles_path = linkedin_articles_path
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
        """Extract and categorize skills from LinkedIn Skills CSV"""
        if not self.skills_path:
            return None
        
        try:
            technical_skills = []
            soft_skills = []
            
            with open(self.skills_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    skill_name = row.get('Name', '').strip()
                    if skill_name:
                        if self._is_soft_skill(skill_name):
                            soft_skills.append(skill_name)
                        else:
                            technical_skills.append(skill_name)

            print(f"Categorized {len(technical_skills)} technical and {len(soft_skills)} soft skills")
            return {
                'technical': self._normalize_list(technical_skills),
                'soft': self._normalize_list(soft_skills)
            }
            
        except Exception as e:
            print(f"Error parsing skills: {str(e)}")
            traceback.print_exc()
            return None

    def parse_linkedin_experience(self):
        """Parse LinkedIn experience from PDF or CSV"""
        if not self.linkedin_exp_path:
            return None
        
        try:
            experiences = []
            
            # Determine file type and parse accordingly
            file_ext = os.path.splitext(self.linkedin_exp_path)[1].lower()
            
            if file_ext == '.pdf':
                experiences = self._parse_linkedin_experience_pdf()
            elif file_ext == '.csv':
                experiences = self._parse_linkedin_experience_csv()
            else:
                print(f"Unsupported file type for LinkedIn experience: {file_ext}")
                return None
                
            if not experiences:
                return None
                
            # Create embeddings for experience descriptions
            if len(experiences) > 0:
                self._create_embeddings(experiences)
                print(f"\nDebug: Created embeddings for {len(experiences)} experiences")
            
            # Extract additional metadata
            titles = [exp['title'] for exp in experiences if exp['title']]
            companies = [exp['company'] for exp in experiences if exp['company']]
            
            # Calculate total duration
            total_duration = self._calculate_total_experience(experiences)
            
            return {
                'experiences': experiences,
                'roles': self._normalize_list(titles),
                'companies': self._normalize_list(companies),
                'total_experiences': len(experiences),
                'total_duration': total_duration
            }
            
        except Exception as e:
            print(f"Error parsing LinkedIn experience: {str(e)}")
            traceback.print_exc()
            return None

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
        """Parse LinkedIn posts from CSV"""
        print("\nDebug: Starting LinkedIn posts parsing...")
        if not self.linkedin_posts_path or not os.path.exists(self.linkedin_posts_path):
            print("Debug: LinkedIn posts path not provided or file doesn't exist")
            return {'posts': [], 'topics': []}
        
        try:
            import pandas as pd
            posts = []
            all_topics = set()
            
            print(f"Debug: Reading CSV from {self.linkedin_posts_path}")
            df = pd.read_csv(self.linkedin_posts_path, encoding='utf-8')
            
            # Verify required columns
            required_cols = ['Date', 'ShareCommentary']
            if not all(col in df.columns for col in required_cols):
                print(f"Error: Missing required columns. Found: {df.columns.tolist()}")
                print(f"Required: {required_cols}")
                return {'posts': [], 'topics': []}
            
            # Sort by date descending but process all posts
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date', ascending=False)
            
            print(f"Debug: Processing {len(df)} posts")
            
            for _, row in df.iterrows():
                post_content = str(row['ShareCommentary']).strip()
                if len(post_content) > 0:
                    # Extract topics and themes
                    post_topics = self._extract_topics(post_content)
                    post_themes = self._extract_post_themes(post_content)
                    
                    # Store full post content but create a preview
                    preview = post_content[:200] + '...' if len(post_content) > 200 else post_content
                    
                    posts.append({
                        'date': row['Date'],
                        'content': post_content,
                        'preview': preview,
                        'topics': post_topics,
                        'themes': post_themes,
                        'embedding': None  # Will be populated by create_embeddings
                    })
                    
                    all_topics.update(post_topics)
            
            # Create embeddings for all posts
            if len(posts) > 0:
                self._create_embeddings(posts)
            
            # Summarize results
            topic_freq = {}
            for post in posts:
                for topic in post['topics']:
                    topic_freq[topic] = topic_freq.get(topic, 0) + 1
            
            print(f"\nDebug: LinkedIn Posts Analysis:")
            print(f"- Total posts processed: {len(posts)}")
            print(f"- Unique topics found: {len(all_topics)}")
            print("- Top topics by frequency:")
            for topic, freq in sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  * {topic}: {freq} mentions")
            
            return {
                'posts': posts,
                'topics': list(all_topics),
                'topic_frequency': topic_freq,
                'total_posts': len(posts)
            }
            
        except Exception as e:
            print(f"Error parsing LinkedIn posts: {str(e)}")
            traceback.print_exc()
            return {'posts': [], 'topics': []}

    def parse_linkedin_data(self):
        """Parse all LinkedIn data sources"""
        print("\n=== LinkedIn Data Parsing ===")
        print(f"LinkedIn Profile Path: {self.linkedin_profile_path}")
        print(f"LinkedIn Posts Path: {self.linkedin_posts_path}")
        print(f"LinkedIn Articles Path: {self.linkedin_articles_path}")
        print(f"LinkedIn Endorsements Path: {self.linkedin_endorsements_path}")
        
        linkedin_data = {}
        
        # Parse experience data from both sources
        experience_data = self.parse_linkedin_experience()
        positions_data = self.parse_linkedin_positions()
        
        # Combine experience data
        if experience_data and positions_data:
            combined_experiences = []
            
            # Add PDF experiences
            if experience_data.get('experiences'):
                combined_experiences.extend(experience_data['experiences'])
                
            # Add CSV positions
            if positions_data.get('positions'):
                combined_experiences.extend(positions_data['positions'])
                
            # Create embeddings for all experiences
            if combined_experiences:
                self._create_embeddings(combined_experiences)
                
            # Update experience data
            linkedin_data['experience'] = {
                'experiences': combined_experiences,
                'roles': self._normalize_list([exp['title'] for exp in combined_experiences if exp.get('title')]),
                'companies': self._normalize_list([exp['company'] for exp in combined_experiences if exp.get('company')]),
                'total_experiences': len(combined_experiences),
                'total_duration': self._calculate_total_experience(combined_experiences)
            }
        
        # Parse other LinkedIn data
        posts_data = self.parse_linkedin_posts()
        if posts_data:
            linkedin_data['posts'] = posts_data
            
        profile_data = self.parse_linkedin_profile()
        if profile_data:
            linkedin_data['profile'] = profile_data
            
        certifications = self.parse_linkedin_certifications()
        if certifications:
            linkedin_data['certifications'] = {'certifications': certifications}
            
        education = self.parse_linkedin_education()
        if education:
            linkedin_data['education'] = education
            
        endorsements = self.parse_linkedin_endorsements()
        if endorsements:
            linkedin_data['endorsements'] = {'endorsements': endorsements}
            
        articles = self.parse_linkedin_articles()
        if articles:
            linkedin_data['articles'] = articles
        
        return linkedin_data

    def parse_linkedin_profile(self):
        """Parse LinkedIn profile data"""
        if not self.linkedin_profile_path:
            return None
        
        try:
            with open(self.linkedin_profile_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                profile_data = next(reader, None)  # Get first row
                if profile_data:
                    return {
                        'name': profile_data.get('First Name', '') + ' ' + profile_data.get('Last Name', ''),
                        'headline': profile_data.get('Headline', ''),
                        'location': profile_data.get('Location', ''),
                        'industry': profile_data.get('Industry', '')
                    }
        except Exception as e:
            print(f"Error parsing LinkedIn profile: {str(e)}")
            traceback.print_exc()
            return None

    def parse_linkedin_articles(self):
        """Parse LinkedIn articles"""
        if not self.linkedin_articles_path:
            return None
        
        try:
            articles = []
            articles_dir = Path(self.linkedin_articles_path)
            
            if articles_dir.is_dir():
                for file in articles_dir.glob('*.html'):
                    with open(file, 'r', encoding='utf-8') as f:
                        soup = BeautifulSoup(f.read(), 'html.parser')
                        title = soup.find('h1').text if soup.find('h1') else file.stem
                        content = soup.get_text()
                        articles.append({
                            'title': title,
                            'content': content,
                            'topics': self._extract_topics(content),
                            'expertise': self._extract_expertise(content)
                        })
            
            return {'articles': articles}
            
        except Exception as e:
            print(f"Error parsing LinkedIn articles: {str(e)}")
            traceback.print_exc()
            return None

    def parse_linkedin_endorsements(self):
        """Parse LinkedIn endorsements"""
        if not self.linkedin_endorsements_path:
            return None
        
        try:
            endorsements = {}
            
            try:
                f, encoding = self._read_csv_with_encoding(self.linkedin_endorsements_path)
                print(f"\nDebug: Successfully opened endorsements CSV with {encoding} encoding")
                
                reader = csv.DictReader(f)
                for row in reader:
                    skill = row.get('Skill Name', '').strip()
                    endorser = row.get('Endorser', '').strip()
                    if skill:
                        if skill not in endorsements:
                            endorsements[skill] = {'count': 0, 'endorsers': set()}
                        endorsements[skill]['count'] += 1
                        if endorser:
                            endorsements[skill]['endorsers'].add(endorser)
                
                f.close()
                
            except Exception as e:
                print(f"Error reading endorsements CSV: {str(e)}")
                traceback.print_exc()
                return None
            
            # Convert sets to lists for JSON serialization
            for skill in endorsements:
                endorsements[skill]['endorsers'] = list(endorsements[skill]['endorsers'])
            
            return endorsements
            
        except Exception as e:
            print(f"Error parsing LinkedIn endorsements: {str(e)}")
            traceback.print_exc()
            return None

    def parse_linkedin_positions(self):
        """Parse LinkedIn positions from CSV"""
        if not self.linkedin_positions_path:
            return None
        
        try:
            positions = []
            
            try:
                f, encoding = self._read_csv_with_encoding(self.linkedin_positions_path)
                print(f"\nDebug: Successfully opened positions CSV with {encoding} encoding")
                
                reader = csv.DictReader(f)
                for row in reader:
                    position = {
                        'title': row.get('Title', '').strip(),
                        'company': row.get('Company Name', '').strip(),
                        'location': row.get('Location', '').strip(),
                        'description': row.get('Description', '').strip(),
                        'started_on': row.get('Started On', '').strip(),
                        'finished_on': row.get('Finished On', '').strip(),
                        'duration': row.get('Duration', '').strip(),
                        'employment_type': row.get('Employment Type', '').strip(),
                        'industry': row.get('Company Industry', '').strip(),
                        'embedding': None  # Will be populated by create_embeddings
                    }
                    positions.append(position)
                    print(f"\nDebug: Parsed position: {position['title']} at {position['company']}")
                
                f.close()
                
            except Exception as e:
                print(f"Error reading positions CSV: {str(e)}")
                traceback.print_exc()
                return None
            
            return {
                'positions': positions,
                'total_positions': len(positions)
            }
            
        except Exception as e:
            print(f"Error parsing LinkedIn positions: {str(e)}")
            traceback.print_exc()
            return None

    def _read_csv_with_encoding(self, file_path):
        """Try different encodings to read CSV file"""
        encodings = ['utf-8', 'utf-16', 'latin1', 'cp1252']
        
        for encoding in encodings:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    # Try to read first line to verify encoding
                    f.readline()
                    # If successful, rewind and return file object
                    f.seek(0)
                    return f, encoding
            except UnicodeDecodeError:
                continue
        
        raise ValueError(f"Could not read file {file_path} with any of the attempted encodings: {encodings}")

    def _parse_linkedin_experience_csv(self):
        """Parse LinkedIn experience from CSV format"""
        try:
            experiences = []
            
            try:
                f, encoding = self._read_csv_with_encoding(self.linkedin_exp_path)
                print(f"\nDebug: Successfully opened experience CSV with {encoding} encoding")
                
                reader = csv.DictReader(f)
                for row in reader:
                    experience = {
                        'title': row.get('Title', '').strip(),
                        'company': row.get('Company Name', '').strip(),
                        'location': row.get('Location', '').strip(),
                        'description': row.get('Description', '').strip(),
                        'started_on': row.get('Started On', '').strip(),
                        'finished_on': row.get('Finished On', '').strip(),
                        'duration': row.get('Duration', '').strip(),
                        'embedding': None
                    }
                    experiences.append(experience)
                    print(f"Debug: Parsed experience: {experience['title']} at {experience['company']}")
                
                f.close()
                
            except Exception as e:
                print(f"Error reading experience CSV: {str(e)}")
                traceback.print_exc()
                return None
            
            return experiences
            
        except Exception as e:
            print(f"Error parsing LinkedIn experience CSV: {str(e)}")
            traceback.print_exc()
            return None

    def _parse_linkedin_experience_pdf(self):
        """Parse LinkedIn experience from PDF format"""
        try:
            import PyPDF2
            import re
            
            experiences = []
            current_experience = {}
            
            with open(self.linkedin_exp_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                # Extract text from all pages
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
                
                # Split into experience sections
                # Look for patterns like "Title at Company" or "Company Name"
                experience_sections = re.split(r'\n(?=[A-Z][^a-z]*(?:at|@)\s+[A-Z]|\d{4}\s*[-–]\s*(?:\d{4}|Present))', text)
                
                for section in experience_sections:
                    if not section.strip():
                        continue
                        
                    exp = {}
                    
                    # Extract title and company
                    title_company_match = re.search(r'(.*?)\s+(?:at|@)\s+(.*?)(?:\n|$)', section)
                    if title_company_match:
                        exp['title'] = title_company_match.group(1).strip()
                        exp['company'] = title_company_match.group(2).strip()
                    else:
                        # Try alternative patterns
                        lines = section.split('\n')
                        exp['title'] = lines[0].strip() if lines else ''
                        exp['company'] = lines[1].strip() if len(lines) > 1 else ''
                    
                    # Extract dates
                    date_match = re.search(r'(\w{3}\s+\d{4})\s*[-–]\s*(\w{3}\s+\d{4}|Present)', section)
                    if date_match:
                        exp['started_on'] = date_match.group(1)
                        exp['finished_on'] = date_match.group(2)
                    
                    # Extract location
                    location_match = re.search(r'\n([^·\n]*(?:Area|Region))[^\n]*', section)
                    if location_match:
                        exp['location'] = location_match.group(1).strip()
                    else:
                        exp['location'] = ''
                    
                    # Extract description
                    # Get text after the header information
                    desc_text = re.split(r'\n\n', section, maxsplit=1)
                    if len(desc_text) > 1:
                        exp['description'] = desc_text[1].strip()
                    else:
                        exp['description'] = ''
                    
                    # Calculate duration
                    exp['duration'] = self._calculate_duration(exp.get('started_on', ''), exp.get('finished_on', ''))
                    
                    # Initialize embedding field
                    exp['embedding'] = None
                    
                    if exp['title'] and exp['company']:  # Only add if we have basic info
                        experiences.append(exp)
                        print(f"\nDebug: Parsed experience: {exp['title']} at {exp['company']}")
            
            return experiences
            
        except Exception as e:
            print(f"Error parsing LinkedIn experience PDF: {str(e)}")
            traceback.print_exc()
            return []

    def parse_linkedin_posts(self):
        """Parse LinkedIn posts from CSV"""
        print("\nDebug: Starting LinkedIn posts parsing...")
        if not self.linkedin_posts_path or not os.path.exists(self.linkedin_posts_path):
            print("Debug: LinkedIn posts path not provided or file doesn't exist")
            return {'posts': [], 'topics': []}
        
        try:
            import pandas as pd
            posts = []
            all_topics = set()
            
            print(f"Debug: Reading CSV from {self.linkedin_posts_path}")
            try:
                f, encoding = self._read_csv_with_encoding(self.linkedin_posts_path)
                df = pd.read_csv(f, encoding=encoding)
                f.close()
            except Exception as e:
                print(f"Error reading posts CSV: {str(e)}")
                return {'posts': [], 'topics': []}
            
            # Verify required columns
            required_cols = ['Date', 'ShareCommentary']
            if not all(col in df.columns for col in required_cols):
                print(f"Error: Missing required columns. Found: {df.columns.tolist()}")
                print(f"Required: {required_cols}")
                return {'posts': [], 'topics': []}
            
            # Sort by date descending
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date', ascending=False)
            
            print(f"Debug: Processing {len(df)} total posts")
            
            # Process all posts but only create embeddings for top 20
            for idx, row in df.iterrows():
                post_content = str(row['ShareCommentary']).strip()
                if len(post_content) > 0:
                    # Extract topics and themes
                    post_topics = self._extract_topics(post_content)
                    post_themes = self._extract_post_themes(post_content)
                    
                    # Store full post content but create a preview
                    preview = post_content[:200] + '...' if len(post_content) > 200 else post_content
                    
                    post = {
                        'date': row['Date'],
                        'content': post_content,
                        'preview': preview,
                        'topics': post_topics,
                        'themes': post_themes,
                        'embedding': None  # Will be populated for top 20 only
                    }
                    
                    posts.append(post)
                    all_topics.update(post_topics)
            
            # Create embeddings only for top 20 recent posts
            if len(posts) > 0:
                top_20_posts = posts[:20]
                self._create_embeddings(top_20_posts)
                print(f"\nDebug: Created embeddings for top {len(top_20_posts)} recent posts")
                
                # Update the posts list with the embedded top 20
                posts[:20] = top_20_posts
        
            # Summarize results
            topic_freq = {}
            for post in posts:
                for topic in post['topics']:
                    topic_freq[topic] = topic_freq.get(topic, 0) + 1
        
            print(f"\nDebug: LinkedIn Posts Analysis:")
            print(f"- Total posts processed: {len(posts)}")
            print(f"- Posts with embeddings: {len([p for p in posts if p.get('embedding')])}")
            print(f"- Unique topics found: {len(all_topics)}")
            print("- Top topics by frequency:")
            for topic, freq in sorted(topic_freq.items(), key=lambda x: x[1], reverse=True)[:10]:
                print(f"  * {topic}: {freq} mentions")
        
            return {
                'posts': posts,
                'topics': list(all_topics),
                'topic_frequency': topic_freq,
                'total_posts': len(posts)
            }
            
        except Exception as e:
            print(f"Error parsing LinkedIn posts: {str(e)}")
            traceback.print_exc()
            return {'posts': [], 'topics': []}

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
        """Extract topics from text using NLP and pattern matching"""
        # Common tech and business topics
        topics = {
            'AI/ML': [
                'AI', 'ML', 'Machine Learning', 'Artificial Intelligence', 'Deep Learning',
                'Neural Networks', 'NLP', 'Computer Vision', 'Data Science',
                'Generative AI', 'LLM', 'Large Language Models'
            ],
            'Cloud/Infrastructure': [
                'Cloud', 'AWS', 'Azure', 'GCP', 'Kubernetes', 'Docker',
                'Microservices', 'DevOps', 'Infrastructure'
            ],
            'Business/Strategy': [
                'Leadership', 'Strategy', 'Innovation', 'Digital Transformation',
                'Product Management', 'Agile', 'Business Development'
            ],
            'Industry': [
                'Healthcare', 'Finance', 'Automotive', 'Retail', 'Manufacturing',
                'Technology', 'Consulting'
            ],
            'Skills': [
                'Project Management', 'Program Management', 'Team Leadership',
                'Architecture', 'Security', 'Data Analytics'
            ]
        }
        
        found_topics = set()
        text = text.lower()
        
        # Extract topics by category
        for category, topic_list in topics.items():
            pattern = '|'.join(map(re.escape, topic_list))
            matches = re.findall(f'\\b({pattern})\\b', text, re.IGNORECASE)
            found_topics.update(matches)
        
        # Extract hashtags
        hashtags = re.findall(r'#(\w+)', text)
        found_topics.update(hashtags)
        
        return list(found_topics)

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

    def _is_soft_skill(self, skill: str) -> bool:
        """Determine if a skill is a soft skill"""
        soft_skill_categories = {
            'leadership': ['leadership', 'management', 'mentoring', 'coaching'],
            'communication': ['communication', 'presentation', 'negotiation'],
            'interpersonal': ['collaboration', 'teamwork', 'relationship'],
            'business': ['strategy', 'business development', 'consulting'],
            'project': ['project management', 'program management', 'agile']
        }

        skill_lower = skill.lower()
        return any(
            any(keyword in skill_lower for keyword in keywords)
            for keywords in soft_skill_categories.values()
        )

    def parse_linkedin_certifications(self):
        """Parse LinkedIn certifications from CSV"""
        if not self.linkedin_certifications_path:
            return None
        
        try:
            certifications = []
            
            try:
                f, encoding = self._read_csv_with_encoding(self.linkedin_certifications_path)
                print(f"\nDebug: Successfully opened certifications CSV with {encoding} encoding")
                
                reader = csv.DictReader(f)
                for row in reader:
                    cert = {
                        'name': row.get('Name', '').strip(),
                        'authority': row.get('Authority', '').strip(),
                        'license_number': row.get('License Number', '').strip(),
                        'time_period': row.get('Time Period', '').strip(),
                        'url': row.get('URL', '').strip()
                    }
                    
                    if cert['name']:  # Only add if we have a name
                        certifications.append(cert)
                        print(f"Debug: Parsed certification: {cert['name']} from {cert['authority']}")
                
                f.close()
                
            except Exception as e:
                print(f"Error reading certifications CSV: {str(e)}")
                traceback.print_exc()
                return None
                
            return {
                'certifications': certifications,
                'total_certifications': len(certifications)
            }
            
        except Exception as e:
            print(f"Error parsing LinkedIn certifications: {str(e)}")
            traceback.print_exc()
            return None

    def parse_linkedin_education(self):
        """Parse LinkedIn education"""
        if not self.linkedin_education_path:
            return None
        
        try:
            education = []
            with open(self.linkedin_education_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    education.append({
                        'degree': row.get('Degree Name', '').strip(),
                        'school': row.get('School Name', '').strip(),
                        'field': row.get('Notes', '').strip()
                    })
                    print(f"Degree: {row.get('Degree Name', '').strip()}")
                    print(f"School: {row.get('School Name', '').strip()}")
            return education
            
        except Exception as e:
            print(f"Error parsing LinkedIn education: {str(e)}")
            traceback.print_exc()
            return None

    def _create_embeddings(self, items):
        """Create embeddings for a list of items with content"""
        try:
            from openai import OpenAI
            client = OpenAI()
            
            for item in items:
                if 'content' in item:
                    text = item['content']
                else:
                    # For experience/position items, combine relevant fields
                    text = f"{item.get('title', '')} at {item.get('company', '')}\n"
                    text += f"Location: {item.get('location', '')}\n"
                    text += f"Duration: {item.get('duration', '')}\n"
                    if item.get('employment_type'):
                        text += f"Type: {item.get('employment_type')}\n"
                    if item.get('industry'):
                        text += f"Industry: {item.get('industry')}\n"
                    text += f"Description: {item.get('description', '')}"
            
                try:
                    response = client.embeddings.create(
                        model="text-embedding-ada-002",
                        input=text[:8000]  # Limit to max tokens
                    )
                    item['embedding'] = response.data[0].embedding
                    print(f"Created embedding for: {item.get('title', 'content item')}")
                except Exception as e:
                    print(f"Error creating embedding: {str(e)}")
                    item['embedding'] = None
                
        except Exception as e:
            print(f"Error initializing embeddings: {str(e)}")

    def _calculate_duration(self, start_date, end_date):
        """Calculate duration between two dates"""
        try:
            from datetime import datetime
            
            # Parse start date
            start = datetime.strptime(start_date, '%b %Y')
            
            # Parse end date
            if end_date.lower() == 'present':
                end = datetime.now()
            else:
                end = datetime.strptime(end_date, '%b %Y')
            
            # Calculate difference in years and months
            years = end.year - start.year
            months = end.month - start.month
            
            if months < 0:
                years -= 1
                months += 12
            
            # Format duration string
            if years > 0 and months > 0:
                return f"{years} yr {months} mo"
            elif years > 0:
                return f"{years} yr"
            else:
                return f"{months} mo"
                
        except Exception as e:
            print(f"Error calculating duration: {str(e)}")
            return ""

    def _calculate_total_experience(self, experiences):
        """Calculate total experience duration"""
        total_months = 0
        
        for exp in experiences:
            duration = exp.get('duration', '')
            if not duration:
                continue
                
            # Extract years and months
            years = re.search(r'(\d+)\s*yr', duration)
            months = re.search(r'(\d+)\s*mo', duration)
            
            if years:
                total_months += int(years.group(1)) * 12
            if months:
                total_months += int(months.group(1))
        
        # Convert back to years and months
        years = total_months // 12
        months = total_months % 12
        
        if years > 0 and months > 0:
            return f"{years} years {months} months"
        elif years > 0:
            return f"{years} years"
        else:
            return f"{months} months"
