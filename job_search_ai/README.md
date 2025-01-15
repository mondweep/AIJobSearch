# Job Search AI

An intelligent job search system that uses AI agents to find, filter, and analyze technology leadership positions.

## Project Structure 

AIJobSearch/
├── job_search_ai/
│   ├── agents/
│   │   ├── __init__.py
│   │   └── job_filter_agent.py      # Main agent for job filtering and analysis
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── config_loader.py         # Loads configuration settings
│   │   ├── job_filter.py            # Job filtering and matching logic
│   │   ├── profile_analyzer.py      # Analyzes professional profiles
│   │   └── profile_parser.py        # Parses various profile data sources
│   ├── tests/
│   │   ├── data/                    # Test data (git-ignored)
│   │   │   ├── cv/
│   │   │   ├── linkedin/
│   │   │   └── medium/
│   │   └── test_*.py               # Test files
│   └── config/
│       └── config.yaml             # Configuration settings
```
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


##Key components and data flow
graph TD
    subgraph Input Sources
        CV[CV/Resume PDFs]
        LI[LinkedIn Data CSVs]
        MD[Medium Articles]
        SK[Skills JSON]
    end

    subgraph Profile Processing
        PP[Profile Parser]
        PA[Profile Analyzer]
        CV & LI & MD & SK --> PP
        PP --> PA
        PA --> PD[(Profile Data)]
    end

    subgraph Job Processing
        JS[Job Search]
        JF[Job Filter]
        JS --> |Raw Job Listings| JF
    end

    subgraph AI Analysis
        LLM[CrewAI LLM]
        JF --> |Job Details| LLM
        PD --> |Profile Analysis| LLM
        LLM --> |Match Analysis| JF
    end

    subgraph Output
        JF --> |Filtered & Ranked Jobs| Results
        Results --> |Match Scores| Display
        Results --> |Skills Gap Analysis| Display
        Results --> |Recommendations| Display
    end

    classDef parser fill:#e1f5fe,stroke:#01579b
    classDef analyzer fill:#fff3e0,stroke:#ff6f00
    classDef llm fill:#f3e5f5,stroke:#7b1fa2
    classDef data fill:#e8f5e9,stroke:#2e7d32
    classDef output fill:#fbe9e7,stroke:#d84315

    class PP,CV,LI,MD,SK parser
    class PA,JF analyzer
    class LLM llm
    class PD,Results data
    class Display output

  1. Input Processing:
    Profile Parser processes multiple data sources
    Each source provides different aspects of professional profile
    Raw data is structured into consistent format
  2. Profile Analysis:
    Profile Analyzer combines parsed data
    Creates comprehensive profile analysis
    Extracts key skills, experience levels, and expertise areas
  3. Job Processing:
    Job Search collects raw job listings
    Job Filter prepares jobs for analysis
    Initial filtering based on basic criteria (salary, location, etc.)
  4. AI Analysis:
    CrewAI LLM performs deep analysis
    Matches profile against job requirements
    Generates detailed compatibility analysis
    Provides recommendations and gap analysis
  5. Output Generation:
    Filtered and ranked job listings
    Match scores and analysis
    Skills gap identification
    Career development recommendations
