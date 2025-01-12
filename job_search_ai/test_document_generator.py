from utils.profile_parser import ProfileParser
from utils.profile_analyzer import ProfileAnalyzer
from utils.job_matcher import JobMatcher
from utils.document_generator import DocumentGenerator
from pathlib import Path

def test_document_generation():
    # Initialize components
    parser = ProfileParser(
        cv_path='tests/data/Mondweep Chakravorty_CVDetails.pdf',
        skills_path='tests/data/LinkedIn Skills.pdf',
        linkedin_exp_path='tests/data/LinkedInExperience _ Mondweep Chakravorty _ LinkedIn (1).pdf'
    )
    
    analyzer = ProfileAnalyzer(parser)
    matcher = JobMatcher(analyzer.analyze_profile())
    
    # Initialize document generator
    generator = DocumentGenerator(analyzer, matcher)
    
    # Sample job description for testing
    sample_job = {
        'title': 'Technical Program Manager',
        'company': 'Tech Corp',
        'description': '''
        We are seeking an experienced Technical Program Manager with:
        - Strong background in Cloud technologies (AWS, Azure)
        - Experience in AI/ML projects
        - Leadership and team management skills
        - Agile project management expertise
        
        Responsibilities include leading technical initiatives, 
        managing cross-functional teams, and driving innovation.
        '''
    }
    
    # Generate documents
    print("\nGenerating CV...")
    cv_content = generator.generate_cv(sample_job['description'])
    
    print("\nGenerating Cover Letter...")
    cover_letter = generator.generate_cover_letter(
        sample_job['description'],
        sample_job['company']
    )
    
    # Save generated documents
    output_dir = Path('tests/output')
    output_dir.mkdir(exist_ok=True)
    
    with open(output_dir / 'generated_cv.html', 'w') as f:
        f.write(cv_content)
    
    with open(output_dir / 'generated_cover_letter.html', 'w') as f:
        f.write(cover_letter)
    
    print("\nDocuments generated successfully!")
    print(f"CV saved to: {output_dir}/generated_cv.html")
    print(f"Cover Letter saved to: {output_dir}/generated_cover_letter.html")

if __name__ == "__main__":
    test_document_generation()
