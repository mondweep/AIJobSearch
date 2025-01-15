from pathlib import Path
import json
from datetime import datetime
import re

class DocumentGenerator:
    def __init__(self, profile_analyzer, job_matcher):
        self.profile_analyzer = profile_analyzer
        self.job_matcher = job_matcher
        self.templates_dir = Path(__file__).parent.parent / 'templates'

    def generate_cv(self, job_description):
        """Generate a tailored CV for a specific job"""
        # Get profile analysis
        profile_data = self.profile_analyzer.analyze_profile()
        
        # Match skills with job requirements
        matched_skills = self._match_skills_for_job(job_description)
        
        # Generate CV content
        cv_content = {
            'personal_info': self._get_personal_info(),
            'professional_summary': self._generate_summary(job_description),
            'highlighted_skills': matched_skills['relevant_skills'],
            'relevant_experience': self._filter_relevant_experience(job_description),
            'achievements': self._select_relevant_achievements(job_description),
            'education': profile_data.get('education', []),
            'certifications': profile_data.get('certifications', [])
        }
        
        return self._apply_cv_template(cv_content)

    def generate_cover_letter(self, job_description, company_name, hiring_manager=None):
        """Generate a tailored cover letter"""
        profile_data = self.profile_analyzer.analyze_profile()
        
        letter_content = {
            'date': datetime.now().strftime('%d-%b-%Y'),
            'greeting': f"Dear {hiring_manager}," if hiring_manager else "Dear Hiring Manager,",
            'opening': self._generate_tailored_opening(
                self._extract_role_from_job(job_description), 
                company_name
            ),
            'background': self._generate_background(profile_data),
            'requirements_experience': self._generate_detailed_body(job_description, profile_data),
            'alignment': self._generate_alignment_paragraph(job_description, profile_data),
            'closing': self._generate_closing(),
            'name': profile_data.get('personal_info', {}).get('name', ''),
            'phone': profile_data.get('personal_info', {}).get('phone', ''),
            'email': profile_data.get('personal_info', {}).get('email', '')
        }
        
        return self._apply_letter_template(letter_content)

    def _match_skills_for_job(self, job_description):
        """Match profile skills with job requirements"""
        profile_data = self.profile_analyzer.analyze_profile()
        all_skills = profile_data['core_competencies']['primary_skills']
        
        # Extract skills from job description
        job_skills = self._extract_skills_from_job(job_description)
        
        # Categorize skills
        return {
            'relevant_skills': [skill for skill in all_skills if skill.lower() in job_skills],
            'transferable_skills': self._identify_transferable_skills(all_skills, job_skills),
            'skill_gaps': [skill for skill in job_skills if skill not in [s.lower() for s in all_skills]]
        }

    def _generate_summary(self, job_description):
        """Generate a more tailored professional summary"""
        profile_data = self.profile_analyzer.analyze_profile()
        job_reqs = self._analyze_job_requirements(job_description)
        
        # Get relevant experience details
        years_exp = profile_data.get('experience_level', {}).get('years', '')
        key_roles = profile_data.get('career_progression', {}).get('key_roles', [])
        domains = profile_data.get('industry_focus', {}).get('primary_industries', [])
        
        summary = f"Experienced {years_exp}+ years technology leader with expertise in "
        
        # Add relevant domains based on job requirements
        relevant_domains = []
        if job_reqs['domain_knowledge'].get('cloud'):
            relevant_domains.append('Cloud Technologies')
        if job_reqs['domain_knowledge'].get('ai_ml'):
            relevant_domains.append('AI/ML')
        if job_reqs['domain_knowledge'].get('agile'):
            relevant_domains.append('Agile Delivery')
            
        summary += f"{', '.join(relevant_domains)}. "
        
        # Add leadership experience if relevant
        if job_reqs['leadership_aspects']:
            leadership_exp = self._extract_leadership_experience(profile_data)
            if leadership_exp:
                summary += f"{leadership_exp} "
                
        return summary.strip()

    def _filter_relevant_experience(self, job_description):
        """Filter and sort relevant experience"""
        profile_data = self.profile_analyzer.analyze_profile()
        experiences = profile_data.get('career_progression', {}).get('career_path', [])
        
        # Score experiences based on relevance to job
        scored_experiences = []
        for exp in experiences:
            relevance_score = self._calculate_experience_relevance(exp, job_description)
            scored_experiences.append((exp, relevance_score))
        
        # Sort by relevance and return top experiences
        return [exp for exp, score in sorted(scored_experiences, key=lambda x: x[1], reverse=True)][:5]

    def _select_relevant_achievements(self, job_description):
        """Select achievements relevant to the job"""
        profile_data = self.profile_analyzer.analyze_profile()
        all_achievements = profile_data.get('leadership_indicators', {}).get('key_achievements', [])
        
        # Score achievements based on relevance
        scored_achievements = []
        for achievement in all_achievements:
            relevance_score = self._calculate_achievement_relevance(achievement, job_description)
            scored_achievements.append((achievement, relevance_score))
        
        # Return top 3 most relevant achievements
        return [ach for ach, score in sorted(scored_achievements, key=lambda x: x[1], reverse=True)][:3]

    def _identify_transferable_skills(self, profile_skills, job_skills):
        """Identify transferable skills"""
        transferable_categories = {
            'leadership': ['team lead', 'management', 'mentoring'],
            'technical': ['programming', 'architecture', 'design'],
            'soft_skills': ['communication', 'problem-solving', 'analytical']
        }
        
        transferable = []
        for skill in profile_skills:
            for category, keywords in transferable_categories.items():
                if any(keyword in skill.lower() for keyword in keywords):
                    transferable.append((skill, category))
        
        return transferable

    def _apply_cv_template(self, content):
        """Apply CV template to content"""
        template_path = self.templates_dir / 'cv_template.html'
        if not template_path.exists():
            return str(content)
            
        with open(template_path) as f:
            template = f.read()
        
        # Format personal info
        template = template.replace('{personal_info.name}', 
            content['personal_info'].get('name', ''))
        template = template.replace('{personal_info.contact}', 
            content['personal_info'].get('contact', ''))
            
        # Format professional summary
        template = template.replace('{professional_summary}', 
            content['professional_summary'])
            
        # Format skills as tags
        skills_html = ''.join([
            f'<span class="skill-tag">{skill}</span>'
            for skill in content['highlighted_skills']
        ])
        template = template.replace('{highlighted_skills}', skills_html)
        
        # Format experience
        experience_html = ''.join([
            f'''
            <div class="experience-item">
                <h3>{exp.get('role', '')}</h3>
                <p class="company">{exp.get('company', '')}</p>
                <p class="duration">{exp.get('duration', '')}</p>
                <ul>
                    {self._format_responsibilities(exp.get('responsibilities', []))}
                </ul>
            </div>
            '''
            for exp in content['relevant_experience']
        ])
        template = template.replace('{relevant_experience}', experience_html)
        
        # Format achievements
        achievements_html = '<ul>' + ''.join([
            f'<li>{achievement}</li>'
            for achievement in content['achievements']
        ]) + '</ul>'
        template = template.replace('{achievements}', achievements_html)
        
        # Format education and certifications
        education_html = '<ul>' + ''.join([
            f'<li>{edu}</li>'
            for edu in content['education']
        ]) + '</ul>'
        certifications_html = '<ul>' + ''.join([
            f'<li>{cert}</li>'
            for cert in content['certifications']
        ]) + '</ul>'
        template = template.replace('{education}', education_html)
        template = template.replace('{certifications}', certifications_html)
        
        return template

    def _format_responsibilities(self, responsibilities):
        """Format responsibilities as list items"""
        return ''.join([
            f'<li>{resp}</li>'
            for resp in responsibilities
        ])

    def _apply_letter_template(self, content):
        """Apply cover letter template to content"""
        template_path = self.templates_dir / 'cover_letter_template.html'
        if not template_path.exists():
            return str(content)
            
        with open(template_path) as f:
            template = f.read()
        
        # Add current date
        from datetime import datetime
        template = template.replace('{date}', 
            datetime.now().strftime('%B %d, %Y'))
            
        # Replace content placeholders
        template = template.replace('{greeting}', content['greeting'])
        template = template.replace('{opening}', content['opening'])
        
        # Format body paragraphs
        body_html = ''.join([
            f'<p>{paragraph}</p>'
            for paragraph in content['body'].split('\n\n')
        ])
        template = template.replace('{body}', body_html)
        
        template = template.replace('{closing}', content['closing'])
        template = template.replace('{signature}', content['signature'])
        
        return template

    def _analyze_job_requirements(self, job_description):
        """Analyze job requirements more thoroughly"""
        requirements = {
            'technical_skills': self._extract_skills_from_job(job_description),
            'leadership_aspects': self._extract_leadership_requirements(job_description),
            'domain_knowledge': self._extract_domain_requirements(job_description)
        }
        return requirements

    def _generate_greeting(self, company_name):
        """Generate appropriate greeting"""
        return f"Dear Hiring Manager at {company_name},"

    def _generate_opening(self, company_name, job_description):
        """Generate opening paragraph"""
        role = self._extract_role_from_job(job_description)
        return f"I am writing to express my strong interest in the {role} position at {company_name}."

    def _generate_letter_body(self, matches, job_analysis):
        """Generate cover letter body"""
        body_paragraphs = []
        
        # First paragraph - Skills match
        relevant_skills = matches['relevant_skills']
        if relevant_skills:
            skills_text = ', '.join(relevant_skills[:3])
            body_paragraphs.append(
                f"With expertise in {skills_text}, I am well-positioned to contribute to your team's success."
            )
        
        # Second paragraph - Experience and achievements
        body_paragraphs.append("My experience includes:")
        achievements = matches.get('achievements', [])
        if achievements:
            for achievement in achievements[:2]:
                body_paragraphs.append(f"• {achievement}")
        else:
            body_paragraphs.append(
                "• Successfully leading cross-functional teams in delivering technical projects\n"
                "• Implementing Agile methodologies to improve project delivery efficiency"
            )
        
        # Third paragraph - Transferable skills
        transferable = matches.get('transferable_skills', [])
        if transferable:
            skills_text = ', '.join(f"{skill}" for skill, _ in transferable[:2])
            body_paragraphs.append(f"Additionally, I bring transferable skills in {skills_text}.")
        
        return '\n\n'.join(body_paragraphs)

    def _generate_closing(self):
        """Generate closing paragraph"""
        return (
            "Thank you for considering my application. I welcome the opportunity "
            "to discuss how my skills and experience align with your needs in "
            "more detail."
        )

    def _get_signature(self):
        """Get signature block"""
        profile_data = self.profile_analyzer.analyze_profile()
        personal_info = profile_data.get('personal_info', {})
        
        return f"""
Best regards,
{personal_info.get('name', '')}
{personal_info.get('email', '')}
{personal_info.get('phone', '')}
{personal_info.get('linkedin', '')}
        """.strip()

    def _extract_skills_from_job(self, job_description):
        """Extract required skills from job description"""
        # Common technical skills to look for
        skill_keywords = [
            'python', 'java', 'aws', 'azure', 'cloud', 'ai', 'ml',
            'devops', 'agile', 'kubernetes', 'docker', 'microservices',
            'leadership', 'management', 'architecture', 'strategy'
        ]
        
        # Convert to lower case for case-insensitive matching
        description_lower = job_description.lower()
        
        # Find all matching skills
        found_skills = set()
        for skill in skill_keywords:
            if skill in description_lower:
                found_skills.add(skill)
        
        return list(found_skills)

    def _extract_experience_requirements(self, job_description):
        """Extract experience requirements from job description"""
        experience_patterns = [
            r'(\d+)[\+]?\s+years?(?:\s+of)?\s+experience',
            r'experience\s+of\s+(\d+)[\+]?\s+years?',
            r'minimum\s+(\d+)[\+]?\s+years?'
        ]
        
        years = []
        for pattern in experience_patterns:
            matches = re.findall(pattern, job_description, re.IGNORECASE)
            years.extend(map(int, matches))
        
        return max(years) if years else None

    def _extract_qualifications(self, job_description):
        """Extract required qualifications from job description"""
        qualification_keywords = [
            "bachelor's", "master's", "phd", "degree",
            "certification", "certified", "qualified"
        ]
        
        qualifications = []
        for line in job_description.lower().split('\n'):
            if any(keyword in line for keyword in qualification_keywords):
                qualifications.append(line.strip())
        
        return qualifications

    def _extract_role_from_job(self, job_description):
        """Extract role title from job description"""
        role_patterns = [
            r'position:\s*(.*?)(?:\.|$)',
            r'role:\s*(.*?)(?:\.|$)',
            r'job title:\s*(.*?)(?:\.|$)'
        ]
        
        for pattern in role_patterns:
            match = re.search(pattern, job_description, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback to first line or generic title
        first_line = job_description.split('\n')[0].strip()
        return first_line if first_line else "the position"

    def _get_personal_info(self):
        """Get personal information from profile"""
        profile_data = self.profile_analyzer.analyze_profile()
        return {
            'name': profile_data.get('personal_info', {}).get('name', ''),
            'contact': profile_data.get('personal_info', {}).get('contact', '')
        }

    def _generate_achievement_highlight(self, job_description):
        """Generate a highlight of relevant achievements"""
        profile_data = self.profile_analyzer.analyze_profile()
        achievements = profile_data.get('leadership_indicators', {}).get('key_achievements', [])
        
        if not achievements:
            return "Proven track record of delivering successful projects."
        
        # Score achievements based on relevance to job description
        scored_achievements = []
        for achievement in achievements:
            score = self._calculate_achievement_relevance(achievement, job_description)
            scored_achievements.append((achievement, score))
        
        # Get the most relevant achievement
        if scored_achievements:
            best_achievement = max(scored_achievements, key=lambda x: x[1])[0]
            return f"Notable achievement includes: {best_achievement}"
        
        return "Demonstrated success in delivering high-impact results."

    def _calculate_achievement_relevance(self, achievement, job_description):
        """Calculate how relevant an achievement is to the job description"""
        # Convert both to lowercase for comparison
        achievement_lower = achievement.lower()
        job_lower = job_description.lower()
        
        # Define relevance keywords from job description
        relevance_keywords = set(word.lower() for word in re.findall(r'\b\w+\b', job_lower))
        
        # Count matching words
        matching_words = sum(1 for word in re.findall(r'\b\w+\b', achievement_lower)
                           if word in relevance_keywords)
        
        return matching_words / len(relevance_keywords) if relevance_keywords else 0

    def _calculate_experience_relevance(self, experience, job_description):
        """Calculate how relevant an experience is to the job description"""
        # Convert both to lowercase for comparison
        exp_lower = str(experience).lower()
        job_lower = job_description.lower()
        
        # Extract key terms from job description
        job_terms = set(re.findall(r'\b\w+\b', job_lower))
        
        # Count matching terms in experience
        matching_terms = sum(1 for term in re.findall(r'\b\w+\b', exp_lower)
                           if term in job_terms)
        
        # Calculate relevance score (0 to 1)
        score = matching_terms / len(job_terms) if job_terms else 0
        
        # Boost score for leadership terms if present
        leadership_terms = {'lead', 'manage', 'direct', 'head', 'oversee'}
        if any(term in exp_lower for term in leadership_terms):
            score *= 1.2
        
        return min(score, 1.0)  # Cap score at 1.0

    def _format_experience(self, experiences):
        """Format experiences with more detail"""
        formatted = []
        for exp in experiences:
            if isinstance(exp, dict):
                company = exp.get('company', '')
                role = exp.get('role', '')
                duration = exp.get('duration', '')
                achievements = exp.get('achievements', [])
                responsibilities = exp.get('responsibilities', [])
                
                exp_html = f"""
                <div class="experience-item">
                    <h3>{role}</h3>
                    <p class="company-duration">{company} | {duration}</p>
                    <ul class="achievements">
                        {self._format_list_items(achievements)}
                        {self._format_list_items(responsibilities)}
                    </ul>
                </div>
                """
                formatted.append(exp_html)
        return '\n'.join(formatted)

    def _format_list_items(self, items):
        """Format list items with bullet points"""
        return ''.join([f'<li>{item}</li>' for item in items if item])

    def _normalize_skills(self, skills):
        """Normalize skill names"""
        skill_mappings = {
            'ai': 'AI',
            'ml': 'ML',
            'aws': 'AWS',
            'azure': 'Azure',
            'devops': 'DevOps'
        }
        return [skill_mappings.get(s.lower(), s) for s in skills]

    def _extract_leadership_requirements(self, job_description):
        """Extract leadership requirements from job description"""
        leadership_keywords = [
            'lead', 'manage', 'direct', 'oversee', 'coordinate',
            'strategic', 'leadership', 'team'
        ]
        found = []
        for line in job_description.lower().split('\n'):
            if any(keyword in line for keyword in leadership_keywords):
                found.append(line.strip())
        return found

    def _extract_domain_requirements(self, job_description):
        """Extract domain-specific requirements"""
        domains = {
            'cloud': ['aws', 'azure', 'cloud', 'saas'],
            'ai_ml': ['ai', 'ml', 'machine learning', 'artificial intelligence'],
            'agile': ['agile', 'scrum', 'kanban', 'sprint'],
            'architecture': ['architect', 'design', 'solution', 'infrastructure']
        }
        
        found_domains = {}
        desc_lower = job_description.lower()
        
        for domain, keywords in domains.items():
            if any(keyword in desc_lower for keyword in keywords):
                found_domains[domain] = True
                
        return found_domains

    def _extract_leadership_experience(self, profile_data):
        """Extract relevant leadership experience"""
        leadership = profile_data.get('leadership_indicators', {})
        team_size = leadership.get('team_size_managed')
        if team_size:
            return f"Experience leading teams of {team_size} across multiple technical initiatives."
        return "Proven track record of leading technical teams and delivering successful projects."

    def _generate_tailored_opening(self, role, company_name):
        """Generate personalized opening paragraph"""
        return (
            f"I am writing to express my keen interest in the {role} position at "
            f"{company_name}. Having reviewed your company's innovative work in "
            f"technology and digital transformation, I am particularly drawn to "
            f"your vision for the future."
        )

    def _generate_detailed_body(self, job_description, profile_data):
        """Generate detailed body with specific examples and metrics"""
        body_paragraphs = []
        
        # Opening paragraph with background
        education = profile_data.get('education', [])
        background = (
            f"My background in {', '.join(education)}, provides a solid foundation for "
            "aligning technology with business strategy. This is reflected in my consistent "
            "track record of driving digital transformation and innovation:"
        )
        body_paragraphs.append(background)
        
        # Extract key requirements from job description
        requirements = self._extract_key_requirements(job_description)
        
        # Match requirements with relevant experiences
        experiences = profile_data.get('experiences', [])
        for req in requirements[:2]:  # Focus on top 2 requirements
            relevant_exp = self._find_relevant_experience(req, experiences)
            if relevant_exp:
                body_paragraphs.append(f"\nRegarding {req}:")
                for exp in relevant_exp[:2]:
                    body_paragraphs.append(f"● At {exp['company']}, {exp['achievement']}")

        # Add team leadership experience
        leadership_exp = self._extract_leadership_metrics(profile_data)
        if leadership_exp:
            body_paragraphs.append("\nMy experience in team leadership includes:")
            for exp in leadership_exp[:2]:
                body_paragraphs.append(f"● {exp}")
        
        return '\n'.join(body_paragraphs)

    def _extract_key_requirements(self, job_description):
        """Extract key requirements from job description"""
        requirements = []
        lines = job_description.split('\n')
        for line in lines:
            if line.strip().startswith('-'):
                req = line.strip('- ').strip()
                requirements.append(req)
        return requirements

    def _find_relevant_experience(self, requirement, experiences):
        """Find experiences relevant to a specific requirement"""
        relevant = []
        req_keywords = set(requirement.lower().split())
        
        for exp in experiences:
            achievements = exp.get('achievements', [])
            for achievement in achievements:
                if any(keyword in achievement.lower() for keyword in req_keywords):
                    relevant.append({
                        'company': exp.get('company', ''),
                        'achievement': achievement
                    })
        return relevant

    def _extract_leadership_metrics(self, profile_data):
        """Extract leadership experience with metrics"""
        leadership = []
        experiences = profile_data.get('experiences', [])
        
        for exp in experiences:
            achievements = exp.get('achievements', [])
            for achievement in achievements:
                if any(term in achievement.lower() for term in ['team', 'lead', 'manage']):
                    if any(char in achievement for char in ['£', '$', '%']):
                        leadership.append(achievement)
        
        return leadership

    def _get_detailed_signature(self, profile_data):
        """Generate detailed signature block"""
        personal_info = profile_data.get('personal_info', {})
        return f"""
Sincerely,
{personal_info.get('name', '')}
{personal_info.get('phone', '')}
{personal_info.get('email', '')}
        """.strip()

    def _generate_executive_summary(self, profile_data):
        """Generate impactful executive summary"""
        achievements = profile_data.get('key_achievements', [])
        revenue_impacts = [ach for ach in achievements if '£' in ach or '$' in ach]
        
        summary = (
            f"I help CIOs at industry-leading global businesses achieve revenue growth "
            f"{self._get_highest_revenue_impact(revenue_impacts)} through targeted digital "
            f"transformation, cloud adoption and technology modernisation by aligning "
            f"technology strategies with business goals, optimising investments and "
            f"delivering complex projects and programmes."
        )
        return summary

    def _format_career_highlights(self, profile_data):
        """Format career highlights with bullet points and metrics"""
        highlights = []
        achievements = profile_data.get('achievements', [])
        
        # Filter and sort achievements by impact
        revenue_achievements = [ach for ach in achievements if '£' in ach or '$' in ach]
        transformation_achievements = [ach for ach in achievements if 'transform' in ach.lower()]
        team_achievements = [ach for ach in achievements if 'team' in ach.lower()]
        
        # Add key metrics-driven achievements first
        for achievement in revenue_achievements[:2]:
            highlights.append(f"● {achievement}")
            
        # Add transformation and team achievements
        if transformation_achievements:
            highlights.append(f"● {transformation_achievements[0]}")
        if team_achievements:
            highlights.append(f"● {team_achievements[0]}")
            
        # Add experience summary
        experience_summary = self._generate_experience_summary(profile_data)
        highlights.append(experience_summary)
        
        return '\n'.join(highlights)

    def _format_career_history(self, profile_data):
        """Format detailed career history with achievements"""
        experiences = profile_data.get('experiences', [])
        formatted_history = []
        
        for exp in experiences:
            company = exp.get('company', '')
            title = exp.get('title', '')
            dates = exp.get('dates', '')
            context = exp.get('context', '')
            objectives = exp.get('objectives', [])
            achievements = exp.get('achievements', [])
            results = exp.get('results', [])
            
            exp_block = f"""
            Employer: {company}
            Job Title: {title}
            Dates: {dates}
            
            {context if context else ''}
            
            {self._format_objectives(objectives)}
            
            {self._format_achievements(achievements)}
            
            Results:
            {self._format_results(results)}
            """
            formatted_history.append(exp_block)
            
        return '\n\n'.join(formatted_history)

    def _format_education_certifications(self, profile_data):
        """Format education and professional certifications"""
        education = profile_data.get('education', [])
        certifications = profile_data.get('certifications', {})
        
        sections = []
        
        if education:
            sections.append("Education")
            for edu in education:
                sections.append(f"● {edu}")
                
        if certifications:
            sections.append("\nProfessional Certifications")
            for category, certs in certifications.items():
                sections.append(f"\n{category}")
                for cert in certs:
                    sections.append(f"● {cert}")
                    
        return '\n'.join(sections)

    def _get_highest_revenue_impact(self, achievements):
        """Extract highest revenue impact from achievements"""
        highest = 0
        for achievement in achievements:
            amounts = re.findall(r'£(\d+(?:\.\d+)?)[MBK]\+?', achievement)
            for amount in amounts:
                value = float(amount)
                if 'B' in achievement:
                    value *= 1000
                highest = max(highest, value)
        return f"£{highest}M+"

    # Additional helper methods as needed
