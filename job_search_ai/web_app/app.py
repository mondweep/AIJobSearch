import os
import sys

# Add parent directory to Python path
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(parent_dir)

import uuid
import shutil
import threading
from datetime import datetime, timezone
from flask import Flask, request, jsonify, render_template, redirect, url_for, send_from_directory, flash
from werkzeug.utils import secure_filename
from job_search_crew import JobSearchCrew
import json
import zipfile

# Initialize Flask app with static folder configuration
app = Flask(__name__, 
    static_url_path='',
    static_folder='static')
app.secret_key = 'your-secret-key-here'  # for session management

# Configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
PROFILE_DOCS_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'profile_docs')
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'txt', 'zip'}

# Create necessary directories
for folder in [UPLOAD_FOLDER, PROFILE_DOCS_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROFILE_DOCS_FOLDER'] = PROFILE_DOCS_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# In-memory stores for session data
search_sessions = {}
search_results = {}
profile_store = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_zip(zip_path, extract_path):
    """Extract ZIP file and return list of extracted files"""
    with zipfile.ZipFile(zip_path, 'r') as zip_ref:
        zip_ref.extractall(extract_path)
    
    # Get list of all extracted files
    extracted_files = []
    for root, _, files in os.walk(extract_path):
        for file in files:
            extracted_files.append(os.path.join(root, file))
    
    return extracted_files

def handle_profile_upload(file, session_id):
    """Handle profile file upload and return file paths"""
    filename = secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{session_id}_{filename}")
    file.save(file_path)
    
    # Create session-specific directory for profile documents
    profile_dir = os.path.join(app.config['PROFILE_DOCS_FOLDER'], session_id)
    if not os.path.exists(profile_dir):
        os.makedirs(profile_dir)
    
    profile_files = []
    
    # If ZIP file, extract contents
    if filename.lower().endswith('.zip'):
        profile_files = extract_zip(file_path, profile_dir)
        # Keep the ZIP file in profile_files
        profile_files.append(file_path)
    else:
        # For non-ZIP files, just add the file
        profile_files.append(file_path)
    
    return profile_files

# Main routes
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/profile')
def profile():
    return render_template('profile_upload.html')

@app.route('/profile-upload')
def profile_upload():
    return render_template('profile_upload.html')

@app.route('/search')
def search():
    session_id = request.args.get('session_id')
    if not session_id or session_id not in search_sessions:
        flash('Please upload your profile first')
        return redirect(url_for('profile_upload'))
    return render_template('search_config.html', session_id=session_id)

@app.route('/search-config')
def search_config():
    session_id = request.args.get('session_id')
    if not session_id or session_id not in search_sessions:
        flash('Please upload your profile first')
        return redirect(url_for('profile_upload'))
    return render_template('search_config.html', session_id=session_id)

@app.route('/results')
def results():
    session_id = request.args.get('session_id')
    if not session_id or session_id not in search_sessions:
        flash('Please upload your profile first')
        return redirect(url_for('profile_upload'))
    return render_template('results.html', session_id=session_id)

@app.route('/job-details/<job_id>')
def job_details(job_id):
    session_id = request.args.get('session_id')
    if not session_id or session_id not in search_sessions:
        return redirect(url_for('profile_upload'))
    
    results = search_results.get(session_id, {})
    job = next((j for j in results.get('jobs', []) if j['id'] == job_id), None)
    
    if not job:
        return redirect(url_for('results', session_id=session_id))
    
    return render_template('job_details.html', job=job)

# API routes
@app.route('/api/upload-profile', methods=['POST'])
def upload_profile():
    try:
        # Check if both files are present
        if 'cv_file' not in request.files or 'linkedin_file' not in request.files:
            return jsonify({
                'status': 'error',
                'message': 'Both CV and LinkedIn data files are required'
            }), 400
        
        cv_file = request.files['cv_file']
        linkedin_file = request.files['linkedin_file']
        
        # Check if files were selected
        if cv_file.filename == '' or linkedin_file.filename == '':
            return jsonify({
                'status': 'error',
                'message': 'No files selected'
            }), 400
        
        # Validate file types
        if not allowed_file(cv_file.filename) or not allowed_file(linkedin_file.filename):
            return jsonify({
                'status': 'error',
                'message': 'Invalid file type'
            }), 400
        
        # Create new session
        session_id = str(uuid.uuid4())
        
        # Handle both file uploads
        cv_files = handle_profile_upload(cv_file, session_id)
        linkedin_files = handle_profile_upload(linkedin_file, session_id)
        
        # Combine all files
        all_files = cv_files + linkedin_files
        
        # Initialize session
        search_sessions[session_id] = {
            'status': 'profile_uploaded',
            'profile_files': all_files,
            'start_time': datetime.now(timezone.utc)
        }
        
        return jsonify({
            'status': 'success',
            'session_id': session_id,
            'message': 'Profile uploaded successfully',
            'file_count': len(all_files)
        })
        
    except Exception as e:
        # Clean up any created directories on error
        profile_dir = os.path.join(app.config['PROFILE_DOCS_FOLDER'], session_id)
        if os.path.exists(profile_dir):
            shutil.rmtree(profile_dir)
            
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

def process_job_search(session_id, profile_files, preferences):
    """Process job search in background using CrewAI"""
    try:
        # Update session status
        search_sessions[session_id]['status'] = 'processing'
        search_sessions[session_id]['message'] = 'Analyzing your profile...'
        
        # Create config for this session
        config = {
            'profile_paths': {},
            'filters': [{
                'min_salary': preferences.get('min_salary'),
                'contract_type': preferences.get('employment_type'),
                'keywords': preferences.get('keywords', [])
            }]
        }
        
        # Process uploaded files
        for file_path in profile_files:
            file_name = os.path.basename(file_path).lower()
            if 'cv' in file_name or 'resume' in file_name:
                config['profile_paths']['cv_template'] = file_path
            elif 'linkedin' in file_name:
                if 'experience' in file_name:
                    config['profile_paths']['linkedin_exp'] = file_path
                elif 'profile' in file_name:
                    config['profile_paths']['linkedin_profile'] = file_path
                elif 'education' in file_name:
                    config['profile_paths']['education'] = file_path
                elif 'certification' in file_name:
                    config['profile_paths']['certification'] = file_path
                elif 'endorsement' in file_name:
                    config['profile_paths']['endorsements'] = file_path
                elif 'position' in file_name:
                    config['profile_paths']['positions'] = file_path
                elif 'article' in file_name:
                    config['profile_paths']['linkedin_articles'] = file_path
                elif 'post' in file_name:
                    config['profile_paths']['linkedin_posts'] = file_path
        
        # Save config for this session
        config_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        os.makedirs(config_dir, exist_ok=True)
        config_path = os.path.join(config_dir, 'config.json')
        with open(config_path, 'w') as f:
            json.dump(config, f)
        
        # Set environment variable for config path
        os.environ['JOB_SEARCH_CONFIG'] = config_path
        
        # Create JobSearchCrew instance
        crew = JobSearchCrew()
        
        # Start the search process
        search_sessions[session_id]['message'] = 'Searching for matching jobs...'
        crew_output = crew.run()
        
        # Parse CrewAI output into structured results
        output_str = str(crew_output)
        
        # Extract jobs from the output
        jobs = []
        current_job = {}
        
        # Split output into lines and parse
        lines = output_str.split('\n')
        for line in lines:
            line = line.strip()
            
            # Skip empty lines and headers
            if not line or line.startswith('#') or line.startswith('*'):
                continue
                
            # Check for job position
            if line.startswith('- **') and ':' not in line:
                if current_job:  # Save previous job if exists
                    jobs.append(current_job)
                current_job = {'title': line.strip('- *')}
                continue
                
            # Parse job details
            if ':' in line:
                key, value = line.split(':', 1)
                key = key.strip('- *').lower().replace(' ', '_')
                value = value.strip()
                if key == 'salary_range':
                    current_job['salary'] = value
                elif key == 'profile_match_score':
                    current_job['match_score'] = float(value)
                else:
                    current_job[key] = value
        
        # Add last job if exists
        if current_job:
            jobs.append(current_job)
            
        # Create structured results
        results = {
            'jobs': jobs,
            'raw_output': output_str,
            'search_criteria': preferences
        }
        
        # Store results in session
        search_sessions[session_id].update({
            'status': 'complete',
            'results': results,
            'message': 'Job search complete',
            'completion_time': datetime.now(timezone.utc)
        })
        
    except Exception as e:
        search_sessions[session_id].update({
            'status': 'error',
            'message': f'Search failed: {str(e)}',
            'error': str(e)
        })
        raise
    finally:
        # Clean up uploaded files and config
        cleanup_dir = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
        if os.path.exists(cleanup_dir):
            shutil.rmtree(cleanup_dir)

@app.route('/api/start-search', methods=['POST'])
def start_search():
    try:
        # Get search preferences from request
        data = request.get_json()
        session_id = request.args.get('session_id')
        
        if not session_id or session_id not in search_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired session. Please upload your profile first.'
            }), 400
        
        # Update session with search preferences
        search_sessions[session_id].update({
            'status': 'searching',
            'preferences': {
                'job_titles': data.get('jobTitles', '').split(','),
                'locations': data.get('locations', '').split(','),
                'min_salary': data.get('minSalary'),
                'max_salary': data.get('maxSalary'),
                'currency': data.get('currency', 'GBP'),
                'employment_type': data.get('employmentType', []),
                'keywords': data.get('keywords', '').split(','),
                'experience_level': data.get('experienceLevel')
            },
            'search_start_time': datetime.now(timezone.utc)
        })
        
        # Start async search process
        thread = threading.Thread(target=process_job_search, args=(
            session_id,
            search_sessions[session_id]['profile_files'],
            search_sessions[session_id]['preferences']
        ))
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'status': 'success',
            'message': 'Search started successfully'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/search-status')
def search_status():
    try:
        session_id = request.args.get('session_id')
        
        if not session_id or session_id not in search_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired session'
            }), 400
            
        session = search_sessions[session_id]
        
        # If we have results, return complete status
        if 'results' in session:
            return jsonify({
                'status': 'complete',
                'message': 'Search complete'
            })
            
        # Otherwise return in progress
        return jsonify({
            'status': session.get('status', 'processing'),
            'message': session.get('message', 'Search in progress...')
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/api/results')
def get_results():
    try:
        session_id = request.args.get('session_id')
        
        if not session_id or session_id not in search_sessions:
            return jsonify({
                'status': 'error',
                'message': 'Invalid or expired session'
            }), 404
        
        session = search_sessions[session_id]
        if 'results' not in session:
            return jsonify({
                'status': 'error',
                'message': 'Search not yet complete'
            }), 400
        
        return jsonify({
            'status': 'success',
            'results': session['results'],
            'searchCriteria': session.get('preferences', {})
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)