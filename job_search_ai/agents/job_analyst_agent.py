from crewai import Agent
from utils.job_summary import JobSummary

class JobAnalystAgent:
    def get_agent(self):
        """Return the CrewAI agent"""
        return Agent(
            role='Job Market Analyst',
            goal='Analyze job market trends and provide insights',
            backstory="""You are an expert at analyzing job market data and identifying 
            trends in technology leadership positions. You understand salary ranges,
            required skills, and market demands.""",
            allow_delegation=False,
            verbose=True
        )

    def __init__(self):
        self.agent = self.get_agent()

    def analyze_jobs(self, filtered_jobs):
        """
        Analyze filtered jobs and provide insights
        """
        analysis = {}
        
        for category, jobs in filtered_jobs.items():
            summary = JobSummary(jobs)
            
            analysis[category] = {
                'total_jobs': len(jobs),
                'salary_stats': summary.get_salary_stats(),
                'top_companies': summary.get_top_companies(),
                'contract_distribution': summary.get_contract_distribution()
            }
            
        return {
            'category_analysis': analysis,
            'recommendations': self._generate_recommendations(analysis)
        }
    
    def _generate_recommendations(self, analysis):
        """
        Generate recommendations based on the analysis
        """
        recommendations = []
        
        for category, data in analysis.items():
            if data['salary_stats']:
                avg_salary = data['salary_stats']['avg']
                if avg_salary > 150000:
                    recommendations.append(f"High potential in {category} with average salary £{avg_salary:,.2f}")
            
            if data['total_jobs'] > 5:
                recommendations.append(f"Strong demand in {category} with {data['total_jobs']} positions")
                
        return recommendations
