// Handle job search functionality
let searchInProgress = false;
let retryCount = 0;
const MAX_RETRIES = 3;

function startJobSearch(event) {
    event.preventDefault();
    
    if (searchInProgress) {
        console.log('Search already in progress');
        return;
    }
    
    // Reset state
    searchInProgress = true;
    retryCount = 0;
    
    // Show loading state
    const spinner = document.getElementById('searchSpinner');
    const results = document.getElementById('searchResults');
    const message = document.getElementById('searchMessage');
    
    spinner.style.display = 'block';
    results.style.display = 'none';
    message.textContent = 'Starting search...';
    message.classList.remove('error');
    
    // Get form data
    const formData = {
        positions: Array.from(document.querySelectorAll('input[name="positions[]"]:checked')).map(el => el.value),
        locations: Array.from(document.querySelectorAll('input[name="locations[]"]:checked')).map(el => el.value),
        contract_types: Array.from(document.querySelectorAll('input[name="contract_types[]"]:checked')).map(el => el.value),
        salary: {
            min: document.querySelector('input[name="min_salary"]').value,
            max: document.querySelector('input[name="max_salary"]').value,
            currency: document.querySelector('select[name="salary_currency"]').value
        },
        keywords: document.querySelector('input[name="keywords"]').value.split(',').map(k => k.trim()).filter(k => k)
    };
    
    // Start search
    fetch('/api/start-search', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(formData)
    })
    .then(response => {
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        return response.json();
    })
    .then(data => {
        if (data.status === 'error') {
            showError(data.message);
            return;
        }
        
        // Store session ID in URL if not already there
        const urlParams = new URLSearchParams(window.location.search);
        if (!urlParams.has('session_id')) {
            urlParams.set('session_id', data.session_id);
            const newUrl = `${window.location.pathname}?${urlParams.toString()}`;
            window.history.pushState({}, '', newUrl);
        }
        
        // Start polling for results
        pollSearchStatus(data.session_id);
    })
    .catch(error => {
        showError('Error starting search: ' + error.message);
        searchInProgress = false;
    });
}

function pollSearchStatus(sessionId) {
    if (!searchInProgress) {
        return;
    }
    
    if (!sessionId) {
        // Try to get session ID from URL if not provided
        const urlParams = new URLSearchParams(window.location.search);
        sessionId = urlParams.get('session_id');
    }
    
    if (!sessionId) {
        showError('No session ID found');
        searchInProgress = false;
        return;
    }
    
    fetch(`/api/search-status?session_id=${sessionId}`)
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            console.log('Search status:', data);  // Debug log
            
            if (data.status === 'error') {
                showError(data.message);
                searchInProgress = false;
                return;
            }
            
            // Update progress message
            document.getElementById('searchMessage').textContent = data.message || 'Searching...';
            
            if (data.status === 'complete') {
                console.log('Search complete, redirecting to results');
                window.location.href = `/results?session_id=${sessionId}`;
                searchInProgress = false;
                return;
            }
            
            // Reset retry count on successful response
            retryCount = 0;
            
            // Continue polling if not complete
            setTimeout(() => pollSearchStatus(sessionId), 2000);
        })
        .catch(error => {
            console.error('Error polling status:', error);  // Debug log
            retryCount++;
            if (retryCount >= MAX_RETRIES) {
                showError('Failed to get search status after multiple attempts');
                searchInProgress = false;
                return;
            }
            setTimeout(() => pollSearchStatus(sessionId), 2000);
        });
}

function showError(message) {
    const spinner = document.getElementById('searchSpinner');
    const messageDiv = document.getElementById('searchMessage');
    
    spinner.style.display = 'none';
    messageDiv.textContent = message;
    messageDiv.classList.add('error');
    searchInProgress = false;
}

// Attach event listeners
document.addEventListener('DOMContentLoaded', () => {
    const searchForm = document.getElementById('searchForm');
    if (searchForm) {
        searchForm.addEventListener('submit', startJobSearch);
    }
    
    // Check if we need to start polling (e.g., page reload during search)
    const urlParams = new URLSearchParams(window.location.search);
    const sessionId = urlParams.get('session_id');
    if (sessionId) {
        searchInProgress = true;
        pollSearchStatus(sessionId);
    }
});

function displayResults(results) {
    const resultsDiv = document.getElementById('searchResults');
    const spinnerDiv = document.getElementById('searchSpinner');
    const messageDiv = document.getElementById('searchMessage');
    
    spinnerDiv.style.display = 'none';
    messageDiv.textContent = '';
    resultsDiv.style.display = 'block';
    
    if (!results || results.length === 0) {
        resultsDiv.innerHTML = '<p class="text-center text-gray-500 my-4">No jobs found matching your criteria.</p>';
        return;
    }
    
    // Sort results by match score
    results.sort((a, b) => b.match_score - a.match_score);
    
    let html = '<div class="job-results grid gap-4 md:grid-cols-2 lg:grid-cols-3">';
    results.forEach(job => {
        html += `
            <div class="job-card bg-white rounded-lg shadow-md p-4">
                <h3 class="text-xl font-semibold text-gray-900">${job.title}</h3>
                <h4 class="text-lg text-gray-600">${job.company}</h4>
                <p class="text-sm text-gray-500"><i class="fas fa-map-marker-alt"></i> ${job.location}</p>
                <p class="text-sm text-gray-500 mt-2"><strong>Salary:</strong> ${formatSalary(job.salary_min, job.salary_max)}</p>
                <p class="text-sm text-gray-500"><strong>Type:</strong> ${job.employment_type}</p>
                <div class="mt-3">
                    <span class="inline-block px-2 py-1 text-sm font-semibold rounded-full 
                        ${job.match_score >= 0.8 ? 'bg-green-100 text-green-800' : 
                          job.match_score >= 0.6 ? 'bg-yellow-100 text-yellow-800' : 
                          'bg-red-100 text-red-800'}">
                        ${formatMatchScore(job.match_score)}% Match
                    </span>
                </div>
                <div class="mt-4">
                    <a href="/job/${job.id}" 
                       class="inline-block w-full text-center px-4 py-2 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700">
                        View Details
                    </a>
                </div>
            </div>
        `;
    });
    html += '</div>';
    
    resultsDiv.innerHTML = html;
}

function formatSalary(min, max) {
    if (!min && !max) return 'Not specified';
    if (min === max) return `£${min.toLocaleString()}`;
    return `£${min.toLocaleString()} - £${max.toLocaleString()}`;
}

function formatMatchScore(score) {
    return (score * 100).toFixed(1);
}

function viewJobDetails(jobId) {
    window.location.href = `/job/${jobId}`;
}
