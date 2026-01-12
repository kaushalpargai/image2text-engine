// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const uploadBtn = document.getElementById('uploadBtn');
const clearBtn = document.getElementById('clearBtn');
const selectedFilesDiv = document.getElementById('selectedFiles');
const progressSection = document.getElementById('progressSection');
const progressFill = document.getElementById('progressFill');
const progressText = document.getElementById('progressText');
const progressStatus = document.getElementById('progressStatus');
const resultsSection = document.getElementById('resultsSection');
const resultsGrid = document.getElementById('resultsGrid');
const totalImagesSpan = document.getElementById('totalImages');
const totalTextSpan = document.getElementById('totalText');

// State
let selectedFiles = [];
let allResults = [];

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    loadExistingResults();
    setupEventListeners();
});

// Event Listeners
function setupEventListeners() {
    // Upload area click
    uploadArea.addEventListener('click', () => fileInput.click());

    // File input change
    fileInput.addEventListener('change', handleFileSelect);

    // Drag and drop
    uploadArea.addEventListener('dragover', handleDragOver);
    uploadArea.addEventListener('dragleave', handleDragLeave);
    uploadArea.addEventListener('drop', handleDrop);

    // Buttons
    uploadBtn.addEventListener('click', handleUpload);
    clearBtn.addEventListener('click', handleClear);
}

// File Selection
function handleFileSelect(e) {
    const files = Array.from(e.target.files);
    addFiles(files);
}

function handleDragOver(e) {
    e.preventDefault();
    uploadArea.classList.add('drag-over');
}

function handleDragLeave(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
}

function handleDrop(e) {
    e.preventDefault();
    uploadArea.classList.remove('drag-over');
    const files = Array.from(e.dataTransfer.files).filter(file => file.type.startsWith('image/'));
    addFiles(files);
}

function addFiles(files) {
    selectedFiles = [...selectedFiles, ...files];
    displaySelectedFiles();
    uploadBtn.disabled = selectedFiles.length === 0;
}

function displaySelectedFiles() {
    selectedFilesDiv.innerHTML = '';
    selectedFiles.forEach((file, index) => {
        const chip = document.createElement('div');
        chip.className = 'file-chip';
        chip.innerHTML = `
            <span>${file.name}</span>
            <span class="file-chip-remove" onclick="removeFile(${index})">×</span>
        `;
        selectedFilesDiv.appendChild(chip);
    });
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    displaySelectedFiles();
    uploadBtn.disabled = selectedFiles.length === 0;
}

// Upload and Process
async function handleUpload() {
    if (selectedFiles.length === 0) return;

    uploadBtn.disabled = true;
    showProgress();

    try {
        // Upload files
        updateProgress(0, 'Uploading files...');
        const uploadedFiles = await uploadFiles();

        // Process files
        updateProgress(50, 'Processing with PaddleOCR...');
        const results = await processFiles(uploadedFiles);

        // Display results
        updateProgress(100, 'Complete!');
        displayResults(results);

        // Clear selection
        selectedFiles = [];
        fileInput.value = '';
        displaySelectedFiles();

        setTimeout(() => {
            hideProgress();
            uploadBtn.disabled = false;
        }, 1000);

    } catch (error) {
        console.error('Error:', error);
        updateProgress(0, 'Error: ' + error.message);
        uploadBtn.disabled = false;
        setTimeout(hideProgress, 3000);
    }
}

async function uploadFiles() {
    const formData = new FormData();
    selectedFiles.forEach(file => formData.append('files', file));

    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    if (!response.ok) throw new Error('Upload failed');

    const data = await response.json();
    return data.files;
}

async function processFiles(files) {
    const response = await fetch('/process', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ files })
    });

    if (!response.ok) throw new Error('Processing failed');

    const data = await response.json();
    return data.results;
}

// Progress
function showProgress() {
    progressSection.style.display = 'block';
    progressSection.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
}

function hideProgress() {
    progressSection.style.display = 'none';
}

function updateProgress(percent, status) {
    progressFill.style.width = percent + '%';
    progressText.textContent = Math.round(percent) + '%';
    progressStatus.textContent = status;
}

// Display Results
function displayResults(results) {
    results.forEach(result => {
        allResults.unshift(result);

        const card = document.createElement('div');
        card.className = 'result-card glass-card';

        card.innerHTML = `
            <div class="result-image-container">
                <img src="${result.image_url}" alt="${result.original_name}" class="result-image">
            </div>
            <div class="result-text-container">
                <div class="result-filename">${result.original_name}</div>
                <div class="result-text">${escapeHtml(result.text)}</div>
                <button class="copy-btn">
                    📋 Copy Text
                </button>
            </div>
        `;

        resultsGrid.insertBefore(card, resultsGrid.firstChild);

        // Add click event listener with the actual text stored in closure
        const copyBtn = card.querySelector('.copy-btn');
        const textToCopy = result.text; // Capture the text for this specific result

        copyBtn.addEventListener('click', function () {
            navigator.clipboard.writeText(textToCopy).then(() => {
                const originalText = this.textContent;
                this.textContent = '✓ Copied!';
                this.style.background = 'var(--gradient-success)';
                this.style.color = 'white';

                setTimeout(() => {
                    this.textContent = originalText;
                    this.style.background = '';
                    this.style.color = '';
                }, 2000);
            });
        });
    });

    updateStats();
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Copy Text
function copyText(button, index) {
    const text = allResults[index].text;
    navigator.clipboard.writeText(text).then(() => {
        const originalText = button.textContent;
        button.textContent = '✓ Copied!';
        button.style.background = 'var(--gradient-success)';
        button.style.color = 'white';

        setTimeout(() => {
            button.textContent = originalText;
            button.style.background = '';
            button.style.color = '';
        }, 2000);
    });
}

// Clear Results
async function handleClear() {
    if (!confirm('Clear all results? This cannot be undone.')) return;

    try {
        await fetch('/results', { method: 'DELETE' });
        allResults = [];
        resultsGrid.innerHTML = '';
        updateStats();
    } catch (error) {
        console.error('Error clearing results:', error);
    }
}

// Load Existing Results
async function loadExistingResults() {
    try {
        const response = await fetch('/results');
        const data = await response.json();

        if (data.results && data.results.length > 0) {
            allResults = data.results;
            data.results.reverse().forEach(result => {
                const card = document.createElement('div');
                card.className = 'result-card glass-card';

                card.innerHTML = `
                    <div class="result-image-container">
                        <img src="${result.image_url}" alt="${result.original_name}" class="result-image">
                    </div>
                    <div class="result-text-container">
                        <div class="result-filename">${result.original_name}</div>
                        <div class="result-text">${escapeHtml(result.text)}</div>
                        <button class="copy-btn" onclick="copyText(this, ${allResults.indexOf(result)})">
                            📋 Copy Text
                        </button>
                    </div>
                `;

                resultsGrid.appendChild(card);
            });

            updateStats();
        }
    } catch (error) {
        console.error('Error loading results:', error);
    }
}

// Update Stats
function updateStats() {
    totalImagesSpan.textContent = allResults.length;

    const totalChars = allResults.reduce((sum, result) => {
        return sum + (result.text ? result.text.length : 0);
    }, 0);

    totalTextSpan.textContent = totalChars.toLocaleString();
}

// Make functions globally available
window.removeFile = removeFile;
window.copyText = copyText;
