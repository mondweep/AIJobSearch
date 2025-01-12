import os
from dotenv import load_dotenv

# Load environment variables
print("Current working directory:", os.getcwd())
env_loaded = load_dotenv()
print("Environment file loaded:", env_loaded)

def test_environment():
    required_packages = [
        'crewai',
        'requests',
        'python-dotenv',
        'beautifulsoup4',
        'pandas',
        'numpy',
        'aiohttp'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing packages: {', '.join(missing_packages)}")
    else:
        print("All required packages are installed!")

    # Test environment variables
    required_env_vars = [
        'OPENAI_API_KEY',
        'ADZUNA_APP_ID',
        'ADZUNA_API_KEY',
        'JOBSERVE_API_KEY',
        'EMAIL_PASSWORD'
    ]
    
    print("\nEnvironment variables found:")
    for var in required_env_vars:
        value = os.getenv(var)
        print(f"{var}: {'[SET]' if value else '[NOT SET]'}")
    
    missing_env_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_env_vars:
        print(f"\nMissing environment variables: {', '.join(missing_env_vars)}")
    else:
        print("\nAll required environment variables are set!")

if __name__ == "__main__":
    test_environment()
