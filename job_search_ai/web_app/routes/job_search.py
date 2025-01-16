from flask import Blueprint, jsonify, request, session
from job_search_crew import JobSearchCrew
from utils.config_loader import ConfigLoader

bp = Blueprint('job_search', __name__)

@bp.route('/api/search', methods=['POST'])
def search():
    try:
        data = request.json
        config = ConfigLoader.load_config()
        
        # Update config with search parameters
        if data and 'criteria' in data:
            config['search_criteria'].update(data['criteria'])
        
        # Initialize and run job search
        crew = JobSearchCrew()
        results = crew.run()
        
        # Store in session
        session['job_results'] = results
        
        return jsonify({
            'status': 'success',
            'results': results
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500