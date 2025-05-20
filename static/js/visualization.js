/**
 * Sudoku Algorithm Visualization
 * This script handles the visualization of the backtracking algorithm for solving Sudoku puzzles.
 */

// Visualization state variables
let visualizationSteps = [];
let decisionTree = [];
let currentStepIndex = 0;
let isPlaying = false;
let playbackInterval = null;
let playbackSpeed = 5; // Default speed (1-10 scale)

// DOM elements for visualization
const visualizeBtn = document.getElementById('visualize-btn');
const visualizationPlaceholder = document.getElementById('visualization-placeholder');
const visualizationControls = document.getElementById('visualization-controls');
const visualizationBoard = document.getElementById('visualization-board');
const stepInfo = document.getElementById('step-info');
const stepMessage = document.getElementById('step-message');
const decisionTreeContainer = document.getElementById('decision-tree-container');
const decisionTreeElement = document.getElementById('decision-tree');
const vizPlayBtn = document.getElementById('viz-play-btn');
const vizPauseBtn = document.getElementById('viz-pause-btn');
const vizStepBtn = document.getElementById('viz-step-btn');
const vizResetBtn = document.getElementById('viz-reset-btn');
const vizSpeedSlider = document.getElementById('viz-speed');
const vizProgress = document.getElementById('viz-progress');

// Initialize the visualization interface
document.addEventListener('DOMContentLoaded', () => {
    setupVisualizationEventListeners();
});

// Set up all event listeners for visualization
function setupVisualizationEventListeners() {
    visualizeBtn.addEventListener('click', startVisualization);
    vizPlayBtn.addEventListener('click', playVisualization);
    vizPauseBtn.addEventListener('click', pauseVisualization);
    vizStepBtn.addEventListener('click', stepVisualization);
    vizResetBtn.addEventListener('click', resetVisualization);
    vizSpeedSlider.addEventListener('input', updatePlaybackSpeed);
}

// Start visualization by fetching data from the server
function startVisualization() {
    // Show loading state
    visualizeBtn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...';
    visualizeBtn.disabled = true;
    
    // Get the current puzzle state
    const puzzleState = [...currentPuzzle]; // From sudoku.js
    
    // Request visualization data from the server
    fetch('/visualize_backtracking', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ puzzle: puzzleState }),
    })
    .then(response => response.json())
    .then(data => {
        // Store the visualization data
        visualizationSteps = data.steps;
        decisionTree = data.decision_tree;
        
        // Reset visualization state
        currentStepIndex = 0;
        isPlaying = false;
        
        // Initialize visualization interface
        initializeVisualizationInterface();
        
        // Render the first step
        renderVisualizationStep(0);
        
        // Reset button state
        visualizeBtn.innerHTML = 'Visualize Backtracking';
        visualizeBtn.disabled = false;
    })
    .catch(error => {
        console.error('Error fetching visualization data:', error);
        visualizeBtn.innerHTML = 'Error - Try Again';
        visualizeBtn.disabled = false;
    });
}

// Initialize the visualization interface
function initializeVisualizationInterface() {
    // Hide placeholder and show visualization components
    visualizationPlaceholder.classList.add('d-none');
    visualizationControls.classList.remove('d-none');
    visualizationBoard.classList.remove('d-none');
    stepInfo.classList.remove('d-none');
    decisionTreeContainer.classList.remove('d-none');
    
    // Create the visualization board
    createVisualizationBoard();
}

// Create the 9x9 Sudoku grid for visualization
function createVisualizationBoard() {
    visualizationBoard.innerHTML = '';
    
    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
            const cell = document.createElement('div');
            cell.className = 'sudoku-cell viz-cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            visualizationBoard.appendChild(cell);
        }
    }
}

// Render a specific step in the visualization
function renderVisualizationStep(stepIndex) {
    if (!visualizationSteps || stepIndex < 0 || stepIndex >= visualizationSteps.length) return;
    
    currentStepIndex = stepIndex;
    const step = visualizationSteps[stepIndex];
    
    // Update the grid
    const cells = visualizationBoard.querySelectorAll('.viz-cell');
    cells.forEach(cell => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        const value = step.grid[row][col];
        
        // Reset cell classes
        cell.className = 'sudoku-cell viz-cell';
        
        // Set cell value
        cell.textContent = value !== 0 ? value : '';
        
        // Highlight the active cell in this step
        if (row === step.row && col === step.col) {
            if (step.is_decision) {
                cell.classList.add('decision');
            } else if (step.is_backtrack) {
                cell.classList.add('backtrack');
            } else {
                cell.classList.add('active');
            }
        }
    });
    
    // Update step message
    stepMessage.textContent = step.message;
    
    // Update step info class based on type
    stepInfo.className = 'alert d-block';
    if (step.is_decision) {
        stepInfo.classList.add('alert-success');
    } else if (step.is_backtrack) {
        stepInfo.classList.add('alert-danger');
    } else {
        stepInfo.classList.add('alert-secondary');
    }
    
    // Update progress bar
    const progress = (stepIndex / (visualizationSteps.length - 1)) * 100;
    vizProgress.style.width = `${progress}%`;
    vizProgress.setAttribute('aria-valuenow', progress);
    
    // Update decision tree visualization
    renderDecisionTree();
}

// Control functions for visualization
function playVisualization() {
    if (isPlaying) return;
    
    isPlaying = true;
    const intervalTime = calculateIntervalTime();
    
    playbackInterval = setInterval(() => {
        const nextIndex = currentStepIndex + 1;
        if (nextIndex >= visualizationSteps.length) {
            pauseVisualization();
            return;
        }
        renderVisualizationStep(nextIndex);
    }, intervalTime);
}

function pauseVisualization() {
    if (!isPlaying) return;
    
    isPlaying = false;
    clearInterval(playbackInterval);
}

function stepVisualization() {
    pauseVisualization();
    
    const nextIndex = currentStepIndex + 1;
    if (nextIndex < visualizationSteps.length) {
        renderVisualizationStep(nextIndex);
    }
}

function resetVisualization() {
    pauseVisualization();
    renderVisualizationStep(0);
}

function updatePlaybackSpeed() {
    playbackSpeed = parseInt(vizSpeedSlider.value);
    
    // If currently playing, restart with new speed
    if (isPlaying) {
        pauseVisualization();
        playVisualization();
    }
}

function calculateIntervalTime() {
    // Convert from 1-10 speed scale to milliseconds (slower to faster)
    // Speed 1 = 1000ms, Speed 10 = 50ms
    return 1050 - (playbackSpeed * 100);
}

// Render the decision tree visualization
function renderDecisionTree() {
    // Basic text-based decision tree for now
    // In a more advanced implementation, this could use D3.js for a graphical tree
    let treeHtml = '';
    
    // Find the decisions up to the current step
    const relevantDecisions = decisionTree.filter(node => node.id <= currentStepIndex);
    
    // Group decisions by their level in the tree
    const decisionsByParent = {};
    relevantDecisions.forEach(decision => {
        if (!decisionsByParent[decision.parent]) {
            decisionsByParent[decision.parent] = [];
        }
        decisionsByParent[decision.parent].push(decision);
    });
    
    // Create a styled tree from the root (parent 0)
    treeHtml = renderTreeNode(0, decisionsByParent, 0);
    
    decisionTreeElement.innerHTML = treeHtml || 'No decision tree data available.';
}

function renderTreeNode(nodeId, decisionsByParent, level) {
    if (!decisionsByParent[nodeId]) return '';
    
    let html = '<ul class="tree-node">';
    
    decisionsByParent[nodeId].forEach(decision => {
        // Determine node style based on success/failure
        let nodeClass = '';
        if (decision.success === true) {
            nodeClass = 'text-success';
        } else if (decision.success === false) {
            nodeClass = 'text-danger';
        }
        
        // Current step indicator
        const isCurrentStep = decision.id === currentStepIndex;
        const currentMarker = isCurrentStep ? ' <span class="text-warning">← Current</span>' : '';
        
        // Create node html
        html += `<li class="${nodeClass}">
            <strong>Cell:</strong> (${decision.row+1}, ${decision.col+1}) 
            <strong>Value:</strong> ${decision.value}
            ${currentMarker}
        </li>`;
        
        // Add children
        const childrenHtml = renderTreeNode(decision.id, decisionsByParent, level + 1);
        if (childrenHtml) {
            html += childrenHtml;
        }
    });
    
    html += '</ul>';
    return html;
}