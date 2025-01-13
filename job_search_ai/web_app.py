from flask import Flask, render_template, jsonify
import subprocess
import threading
import queue
import time
from datetime import datetime
import os

app = Flask(__name__)
output_queue = queue.Queue()

def run_job_search():
    """Run the job search script and capture output"""
    script_path = os.path.join(os.path.dirname(__file__), 'job_search_crew.py')
    process = subprocess.Popen(
        ['python', script_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    for line in process.stdout:
        output_queue.put(line)
    
    process.wait()
    output_queue.put(None)  # Signal completion

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/run-search', methods=['GET', 'POST'])
def run_search():
    thread = threading.Thread(target=run_job_search)
    thread.start()
    return jsonify({"status": "started"})

@app.route('/get-output')
def get_output():
    lines = []
    while True:
        try:
            line = output_queue.get_nowait()
            if line is None:
                return jsonify({"complete": True, "lines": lines})
            lines.append(line)
        except queue.Empty:
            return jsonify({"complete": False, "lines": lines})

if __name__ == '__main__':
    app.run(debug=True)
