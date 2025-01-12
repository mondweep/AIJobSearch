# Job Search AI

An intelligent job search system that uses AI agents to find, filter, and analyze technology leadership positions.

## Project Structure 

job_search_ai/
├── services/
│ ├── init.py
│ ├── adzuna_service.py # Handles Adzuna API integration
│ └── jobserve_service.py # (Future) JobServe API integration
├── utils/
│ ├── init.py
│ ├── job_filter.py # Job filtering utilities
│ └── job_summary.py # Job analysis and reporting
├── agents/
│ ├── init.py
│ ├── job_search_agent.py # AI agent for job searching
│ ├── job_filter_agent.py # AI agent for filtering results
│ └── job_analyst_agent.py # AI agent for market analysis
├── job_search_crew.py # Orchestrates AI agents
├── main.py # Main application entry point
└── test_env.py # Environment setup verification

## Features
- Automated job search using the Adzuna API
- Intelligent filtering based on:
  - Salary requirements
  - Contract types
  - Keywords and skills
- Market analysis including:
  - Salary statistics
  - Top hiring companies
  - Contract type distribution
- AI-powered insights using CrewAI agents

## Setup
1. Install required packages:
bash
pip install crewai python-dotenv requests beautifulsoup4 pandas numpy aiohttp langchain

2. Create a `.env` file with your API keys:
```
OPENAI_API_KEY=your_openai_api_key
ADZUNA_API_KEY=your_adzuna_api_key
JOBSERVE_API_KEY=your_jobserve_api_key
EMAIL_PASSWORD=your_email_password
```

3. Verify setup:
```bash
python test_env.py
```

## Usage
Run the main script to start the job search:
```bash
python main.py
```

## Components

### Services
- **AdzunaService**: Handles job searches through the Adzuna API
- **JobServeService**: (Planned) Will add JobServe integration

### Utilities
- **JobFilter**: Filters jobs based on salary, contract type, and keywords
- **JobSummary**: Generates analysis and insights from job data

### AI Agents
- **JobSearchAgent**: Specializes in finding relevant job postings
- **JobFilterAgent**: Filters and ranks job listings
- **JobAnalystAgent**: Analyzes market trends and provides insights

### Crew
The `JobSearchCrew` orchestrates the AI agents to:
1. Search for jobs matching criteria
2. Filter and rank the results
3. Provide market analysis and recommendations

## Current Focus
- Technology leadership positions
- UK market (primarily London)
- Roles including:
  - Head of Technology
  - Head of Cloud
  - Head of Cyber Security
  - AI Program Manager
  - Technology Directors
  - CISOs

## Future Enhancements
- Additional job board integrations
- More sophisticated filtering algorithms
- Enhanced market analysis
- Email notifications for new matches
