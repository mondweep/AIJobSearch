from utils.profile_parser import ProfileParser
from pathlib import Path

def test_profile_parser():
    # Get the path to data directory
    data_dir = Path(__file__).parent / 'tests' / 'data'
    
    # Define file paths with actual file names
    cv_template = data_dir / 'Mondweep Chakravorty_CVDetails.pdf'
    cv_long = data_dir / 'Mondweep ChakravortyMaster_CV_LongVersion.pdf'
    cv_more = data_dir / 'Mondweep ChakravortyCV_MoreDetails.docx.pdf'
    skills_file = data_dir / 'LinkedIn Skills.pdf'
    linkedin_posts = data_dir / 'LinkedIn Posts.pdf'
    linkedin_exp = data_dir / 'LinkedInExperience _ Mondweep Chakravorty _ LinkedIn (1).pdf'
    medium_profile = data_dir / 'Medium Profile.pdf'
    
    # Verify files exist
    files_to_check = {
        'CV Template': cv_template,
        'Long CV': cv_long,
        'More Details CV': cv_more,
        'Skills': skills_file,
        'LinkedIn Posts': linkedin_posts,
        'LinkedIn Experience': linkedin_exp,
        'Medium Profile': medium_profile
    }
    
    for name, file_path in files_to_check.items():
        if not file_path.exists():
            print(f"Error: {name} not found at '{file_path}'")
            return
        else:
            print(f"Found {name} at '{file_path}'")
    
    # Initialize parser with files
    parser = ProfileParser(
        cv_path=str(cv_template),
        cv_long_path=str(cv_long),
        cv_more_path=str(cv_more),
        skills_path=str(skills_file),
        linkedin_posts_path=str(linkedin_posts),
        linkedin_exp_path=str(linkedin_exp),
        medium_path=str(medium_profile)
    )
    
    print("\nTesting Profile Analysis...")
    
    # Test CV parsing
    print("\n1. Analyzing CV Template...")
    cv_data = parser.parse_cv()
    if cv_data:
        print("Skills found:", cv_data.get('skills', []))
        print("Experiences found:", cv_data.get('experiences', []))
    
    # Test Skills parsing
    print("\n2. Analyzing Skills...")
    skills_data = parser.parse_skills()
    if skills_data:
        print("Technical Skills:", skills_data.get('technical', []))
        print("Soft Skills:", skills_data.get('soft', []))
    
    # Test Medium articles
    print("\n3. Analyzing Medium Profile...")
    medium_data = parser.parse_medium_profile()
    if medium_data:
        print("Article Topics:", medium_data.get('topics', []))
        print("Areas of Expertise:", medium_data.get('expertise', []))

if __name__ == "__main__":
    test_profile_parser()
