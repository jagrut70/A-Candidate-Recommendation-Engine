// Candidate Recommendation Engine - JavaScript

let uploadedCandidates = [];
let manualCandidates = [];

// Initialize the application
document.addEventListener('DOMContentLoaded', function() {
    try {
        // Show loading screen for 2 seconds
        setTimeout(() => {
            const loadingScreen = document.getElementById('loadingScreen');
            const mainApp = document.getElementById('mainApp');
            
            if (loadingScreen && mainApp) {
                loadingScreen.style.opacity = '0';
                setTimeout(() => {
                    loadingScreen.style.display = 'none';
                    mainApp.style.display = 'flex';
                    mainApp.style.opacity = '0';
                    setTimeout(() => {
                        mainApp.style.opacity = '1';
                    }, 50);
                }, 500);
            }
        }, 2000);
        
        setupEventListeners();
        setupTabSwitching();
        updateRecommendButton();
        
        // Set up button click listener
        const recommendBtn = document.getElementById('recommendBtn');
        if (recommendBtn) {
            recommendBtn.addEventListener('click', function(e) {
                generateRecommendations();
            });
        } else {
            console.error('Recommend button not found!');
        }
        
        // Set up help button
        const helpBtn = document.querySelector('.btn-help');
        if (helpBtn) {
            helpBtn.addEventListener('click', function() {
                const helpModal = new bootstrap.Modal(document.getElementById('helpModal'));
                helpModal.show();
            });
        }
        
    } catch (error) {
        console.error('Error in DOMContentLoaded:', error);
    }
});

function setupEventListeners() {
    // Job description input listener
    document.getElementById('jobDescription').addEventListener('input', function() {
        updateCharCount();
        updateRecommendButton();
    });
    
    // File input listener
    document.getElementById('resumeFiles').addEventListener('change', function() {
        displaySelectedFiles();
        updateRecommendButton();
    });
    
    // Drag and drop functionality
    setupDragAndDrop();
}

function setupTabSwitching() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            
            // Remove active class from all tabs
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));
            
            // Add active class to clicked tab
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');
            
            updateRecommendButton();
        });
    });
}

function setupDragAndDrop() {
    const uploadArea = document.getElementById('uploadArea');
    const fileInput = document.getElementById('resumeFiles');
    
    // Make the entire upload area clickable to trigger file selection
    uploadArea.addEventListener('click', function(e) {
        // Don't trigger if clicking on the file input itself
        if (e.target !== fileInput) {
            fileInput.click();
        }
    });
    
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, preventDefaults, false);
    });
    
    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }
    
    ['dragenter', 'dragover'].forEach(eventName => {
        uploadArea.addEventListener(eventName, highlight, false);
    });
    
    ['dragleave', 'drop'].forEach(eventName => {
        uploadArea.addEventListener(eventName, unhighlight, false);
    });
    
    function highlight(e) {
        uploadArea.classList.add('dragover');
    }
    
    function unhighlight(e) {
        uploadArea.classList.remove('dragover');
    }
    
    uploadArea.addEventListener('drop', handleDrop, false);
    
    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        fileInput.files = files;
        displaySelectedFiles();
        updateRecommendButton();
    }
}

function updateCharCount() {
    const textarea = document.getElementById('jobDescription');
    const charCount = textarea.value.length;
    document.querySelector('.char-count').textContent = charCount;
}

function displaySelectedFiles() {
    const fileInput = document.getElementById('resumeFiles');
    const uploadedFilesDiv = document.getElementById('uploadedFiles');
    const files = fileInput.files;
    
    if (files.length === 0) {
        uploadedFilesDiv.innerHTML = '';
        return;
    }
    
    let html = '';
    for (let file of files) {
        html += `
            <div class="file-item">
                <div class="file-icon">
                    <i class="fas fa-file-text"></i>
                </div>
                <div class="file-info">
                    <div class="file-name">${file.name}</div>
                    <div class="file-size">${formatFileSize(file.size)}</div>
                </div>
            </div>
        `;
    }
    uploadedFilesDiv.innerHTML = html;
}

function updateRecommendButton() {
    const jobDescription = document.getElementById('jobDescription').value.trim();
    const fileInput = document.getElementById('resumeFiles');
    const activeTabElement = document.querySelector('.tab-button.active');
    
    if (!activeTabElement) {
        console.error('No active tab found!');
        return;
    }
    
    const activeTab = activeTabElement.getAttribute('data-tab');
    
    let hasCandidates = false;
    
    if (activeTab === 'file-upload') {
        hasCandidates = fileInput.files.length > 0;
    } else if (activeTab === 'manual-input') {
        hasCandidates = manualCandidates.length > 0;
    }
    
    const recommendBtn = document.getElementById('recommendBtn');
    const shouldEnable = jobDescription && hasCandidates;
    
    if (recommendBtn) {
        recommendBtn.disabled = !shouldEnable;
    } else {
        console.error('Recommend button not found in updateRecommendButton!');
    }
}

// File upload functionality
async function uploadFiles() {
    console.log('uploadFiles function called');
    const fileInput = document.getElementById('resumeFiles');
    const files = fileInput.files;
    
    console.log('Upload button clicked');
    console.log('Files selected:', files.length);
    
    if (files.length === 0) {
        showToast('Please select at least one file to upload.', 'warning');
        return;
    }
    
    const formData = new FormData();
    for (let file of files) {
        formData.append('resumes', file);
        console.log('Adding file to form data:', file.name);
    }
    
    try {
        showLoading(true);
        console.log('Sending upload request to /upload');
        
        const response = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        console.log('Response status:', response.status);
        const result = await response.json();
        console.log('Response data:', result);
        
        if (response.ok) {
            uploadedCandidates = result.candidates;
            showToast(`Successfully uploaded ${result.candidates.length} files!`, 'success');
            updateRecommendButton();
        } else {
            showToast(result.error || 'Upload failed. Please try again.', 'danger');
        }
    } catch (error) {
        console.error('Upload error:', error);
        showToast('An error occurred during upload. Please try again.', 'danger');
    } finally {
        showLoading(false);
    }
}

// Manual input functionality
function addCandidateInput() {
    const container = document.getElementById('candidateInputs');
    const candidateDiv = document.createElement('div');
    candidateDiv.className = 'candidate-input-card';
    candidateDiv.innerHTML = `
        <div class="candidate-header">
            <div class="candidate-avatar">
                <i class="fas fa-user"></i>
            </div>
            <div class="candidate-info">
                <input type="text" class="form-control-custom candidate-name" 
                       placeholder="Candidate Name">
                <textarea class="form-control-custom candidate-resume" rows="4" 
                          placeholder="Enter resume content..."></textarea>
            </div>
            <button type="button" class="remove-candidate" onclick="removeCandidateInput(this)">
                <i class="fas fa-times"></i>
            </button>
        </div>
    `;
    container.appendChild(candidateDiv);
}

function removeCandidateInput(button) {
    button.closest('.candidate-input-card').remove();
    updateRecommendButton();
}

function processManualInput() {
    const candidateInputs = document.querySelectorAll('.candidate-input-card');
    manualCandidates = [];
    
    candidateInputs.forEach((input, index) => {
        const nameInput = input.querySelector('.candidate-name');
        const resumeInput = input.querySelector('.candidate-resume');
        
        const name = nameInput.value.trim();
        const resume = resumeInput.value.trim();
        
        if (name && resume) {
            manualCandidates.push({
                name: name,
                resume: resume
            });
        }
    });
    
    if (manualCandidates.length === 0) {
        showToast('Please enter at least one candidate with both name and resume content.', 'warning');
        return;
    }
    
    showToast(`Processed ${manualCandidates.length} candidates!`, 'success');
    updateRecommendButton();
}

// Generate recommendations
async function generateRecommendations() {
    const jobDescription = document.getElementById('jobDescription').value.trim();
    const activeTab = document.querySelector('.tab-button.active').getAttribute('data-tab');
    
    if (!jobDescription) {
        showToast('Please enter a job description.', 'warning');
        return;
    }
    
    let candidates = [];
    if (activeTab === 'file-upload') {
        // Initialize uploadedCandidates if undefined
        if (!uploadedCandidates) {
            uploadedCandidates = [];
        }
        
        // Check if files are selected but not uploaded
        const fileInput = document.getElementById('resumeFiles');
        if (fileInput.files.length > 0 && uploadedCandidates.length === 0) {
            showToast('Uploading files automatically...', 'info');
            await uploadFiles();
            if (!uploadedCandidates || uploadedCandidates.length === 0) {
                showToast('Failed to upload files. Please try again.', 'danger');
                return;
            }
        }
        
        if (uploadedCandidates.length === 0) {
            showToast('Please upload candidate files first.', 'warning');
            return;
        }
        candidates = uploadedCandidates;
    } else if (activeTab === 'manual-input') {
        // Initialize manualCandidates if undefined
        if (!manualCandidates) {
            manualCandidates = [];
        }
        
        if (manualCandidates.length === 0) {
            showToast('Please process manual input first.', 'warning');
            return;
        }
        candidates = manualCandidates;
    }
    
    try {
        showLoading(true);
        showResultsLoading();
        
        let response;
        if (activeTab === 'file-upload') {
            response = await fetch('/recommend', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_description: jobDescription
                })
            });
        } else {
            response = await fetch('/manual-input', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    job_description: jobDescription,
                    candidates: candidates
                })
            });
        }
        
        const result = await response.json();
        
        if (response.ok) {
            displayRecommendations(result.recommendations, result.total_candidates);
        } else {
            showToast(result.error || 'Failed to generate recommendations.', 'danger');
        }
    } catch (error) {
        console.error('Recommendation error:', error);
        showToast('An error occurred while generating recommendations.', 'danger');
    } finally {
        showLoading(false);
    }
}

// Display recommendations
function displayRecommendations(recommendations, totalCandidates) {
    const resultsSection = document.getElementById('resultsSection');
    
    // Hide loading section
    hideResultsLoading();
    
    if (recommendations.length === 0) {
        resultsSection.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">
                    <i class="fas fa-exclamation-triangle"></i>
                </div>
                <h4>No Recommendations Found</h4>
                <p>Please check your input data and try again.</p>
            </div>
        `;
        return;
    }
    
    let html = `
        <div class="mb-4">
            <h4><i class="fas fa-chart-line"></i> Analysis Results</h4>
            <p class="text-muted">Analyzed ${totalCandidates} candidates, showing top ${recommendations.length} matches</p>
        </div>
    `;
    
    recommendations.forEach((candidate, index) => {
        const similarityScore = (candidate.similarity_score * 100).toFixed(1);
        const similarityClass = getSimilarityClass(candidate.similarity_score);
        const isTopMatch = index === 0;
        
        html += `
            <div class="candidate-result ${isTopMatch ? 'top-match' : ''}">
                <div class="candidate-header-result">
                    <div class="candidate-info-result">
                        <div class="candidate-avatar-result">
                            ${candidate.name.charAt(0).toUpperCase()}
                        </div>
                        <div class="candidate-details">
                            <h5>${candidate.name}</h5>
                            <div class="candidate-file">${candidate.filename || 'Manual Input'}</div>
                        </div>
                    </div>
                    <div class="similarity-score-container">
                        <div class="similarity-score ${similarityClass}">${similarityScore}%</div>
                        <div class="score-label">Match Score</div>
                    </div>
                </div>
                <div class="ai-summary">
                    <strong>AI Analysis:</strong> ${candidate.ai_summary}
                </div>
            </div>
        `;
    });
    
    resultsSection.innerHTML = html;
}

// Helper functions
function getSimilarityClass(score) {
    if (score >= 0.7) return 'high';
    if (score >= 0.4) return 'medium';
    return 'low';
}

function showLoading(show) {
    const recommendBtn = document.getElementById('recommendBtn');
    if (show) {
        recommendBtn.classList.add('loading');
    } else {
        recommendBtn.classList.remove('loading');
    }
}

function showResultsLoading() {
    const loadingSection = document.getElementById('loadingSection');
    const resultsSection = document.getElementById('resultsSection');
    
    loadingSection.style.display = 'block';
    resultsSection.innerHTML = '';
}

function hideResultsLoading() {
    const loadingSection = document.getElementById('loadingSection');
    loadingSection.style.display = 'none';
}

function showToast(message, type) {
    const toastContainer = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="fas fa-${getToastIcon(type)} me-2"></i>
            <span>${message}</span>
        </div>
    `;
    
    toastContainer.appendChild(toast);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (toast.parentNode) {
            toast.remove();
        }
    }, 5000);
}

function getToastIcon(type) {
    switch(type) {
        case 'success': return 'check-circle';
        case 'warning': return 'exclamation-triangle';
        case 'danger': return 'times-circle';
        default: return 'info-circle';
    }
}

// Utility function to format file size
function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
} 