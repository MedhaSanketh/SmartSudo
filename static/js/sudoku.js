// Global variables to store the game state
let currentPuzzle = [];
let originalPuzzle = []; // Store the original puzzle for AI hints
let currentSolution = [];
let selectedCell = null;
let currentDifficulty = 'medium';
let currentGridType = '3x3';
let currentGridSize = 9;
let currentBoxSize = 3;
let fixedCells = [];

// DOM elements
const gameBoard = document.getElementById('game-board');
const numberButtons = document.querySelectorAll('.number-btn');
const eraseButton = document.getElementById('erase-btn');
const newGameButton = document.getElementById('new-game-btn');
const aiHintButton = document.getElementById('ai-hint-btn');
const solutionHintButton = document.getElementById('solution-hint-btn');
const checkButton = document.getElementById('check-btn');
const difficultyOptions = document.querySelectorAll('.difficulty-option');
const currentDifficultyElement = document.getElementById('current-difficulty');
const gridSizeOptions = document.querySelectorAll('.grid-size-option');
const currentGridSizeElement = document.getElementById('current-grid-size');
const gameCompletedModal = new bootstrap.Modal(document.getElementById('gameCompletedModal'));
const newGameAfterWinButton = document.getElementById('newGameAfterWin');
const hintDisplay = document.getElementById('hint-display');
const hintMessage = document.getElementById('hint-message');
const hintTechnique = document.getElementById('hint-technique');

// Initialize the game
document.addEventListener('DOMContentLoaded', () => {
    initializeGame();
    setupEventListeners();
});

// Initialize the game board and fetch a new puzzle
function initializeGame() {
    createGameBoard();
    fetchNewPuzzle();
}

// Create the variable-size Sudoku grid
function createGameBoard() {
    gameBoard.innerHTML = '';
    
    // Update board classes for grid size
    gameBoard.className = `sudoku-board grid-${currentGridType}`;
    
    for (let row = 0; row < currentGridSize; row++) {
        for (let col = 0; col < currentGridSize; col++) {
            const cell = document.createElement('div');
            cell.className = 'sudoku-cell';
            cell.dataset.row = row;
            cell.dataset.col = col;
            gameBoard.appendChild(cell);
        }
    }
}

// Fetch a new puzzle from the server
function fetchNewPuzzle() {
    fetch('/new_puzzle', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
            difficulty: currentDifficulty,
            grid_type: currentGridType
        })
    })
    .then(response => response.json())
    .then(data => {
        currentPuzzle = data.puzzle;
        originalPuzzle = JSON.parse(JSON.stringify(data.puzzle));
        currentSolution = data.solution;
        currentDifficulty = data.difficulty;
        currentGridSize = data.grid_size;
        currentBoxSize = data.box_size;
        currentGridType = data.grid_type;
        
        createGameBoard(); // Recreate board with new size
        renderPuzzle();
        updateNumberPad();
        fixedCells = [];
        
        // Mark initial cells as fixed
        for (let row = 0; row < currentGridSize; row++) {
            for (let col = 0; col < currentGridSize; col++) {
                if (currentPuzzle[row][col] !== 0) {
                    fixedCells.push(`${row}-${col}`);
                }
            }
        }
            
            // Hide hint display when starting a new puzzle
            hideHintDisplay();
        })
        .catch(error => console.error('Error fetching puzzle:', error));
}

// Update the number pad based on current grid size
function updateNumberPad() {
    const numberPad = document.querySelector('.number-pad .row');
    if (!numberPad) return;
    
    numberPad.innerHTML = '';
    
    // Add number buttons based on grid size
    for (let i = 1; i <= currentGridSize; i++) {
        const col = document.createElement('div');
        col.className = 'col';
        
        const button = document.createElement('button');
        button.className = 'btn btn-outline-secondary w-100 number-btn';
        button.setAttribute('data-number', i);
        button.textContent = i;
        
        col.appendChild(button);
        numberPad.appendChild(col);
    }
    
    // Add erase button
    const eraseCol = document.createElement('div');
    eraseCol.className = 'col';
    
    const eraseButton = document.createElement('button');
    eraseButton.className = 'btn btn-outline-danger w-100';
    eraseButton.id = 'erase-btn';
    eraseButton.innerHTML = '<i class="fas fa-eraser"></i>';
    
    eraseCol.appendChild(eraseButton);
    numberPad.appendChild(eraseCol);
    
    // Re-attach event listeners
    setupNumberPadListeners();
}

// Setup event listeners for number pad buttons
function setupNumberPadListeners() {
    // Number buttons event listeners
    document.querySelectorAll('.number-btn').forEach(button => {
        button.addEventListener('click', () => {
            const number = parseInt(button.dataset.number);
            inputNumber(number);
        });
    });
    
    // Erase button event listener
    const eraseButton = document.getElementById('erase-btn');
    if (eraseButton) {
        eraseButton.addEventListener('click', eraseNumber);
    }
}

// Render the current puzzle state on the board
function renderPuzzle() {
    // Get all the cells
    const cells = document.querySelectorAll('.sudoku-cell');
    
    // Update each cell with the current puzzle state
    cells.forEach(cell => {
        const row = parseInt(cell.dataset.row);
        const col = parseInt(cell.dataset.col);
        const value = currentPuzzle[row][col];
        
        // Clear previous state classes
        cell.classList.remove('fixed', 'selected', 'highlighted', 'same-number', 'valid', 'invalid', 'hint');
        
        // Set cell value
        cell.textContent = value !== 0 ? value : '';
        
        // Mark fixed cells
        if (fixedCells.includes(`${row}-${col}`)) {
            cell.classList.add('fixed');
        }
    });
}

// Handle cell selection
function selectCell(cell) {
    // Clear previous selection
    if (selectedCell) {
        selectedCell.classList.remove('selected');
    }
    
    // Remove highlighting from all cells
    document.querySelectorAll('.sudoku-cell').forEach(cell => {
        cell.classList.remove('highlighted', 'same-number');
    });
    
    // If the cell is fixed, don't select it
    if (cell.classList.contains('fixed')) {
        selectedCell = null;
        return;
    }
    
    // Set the new selected cell
    selectedCell = cell;
    cell.classList.add('selected');
    
    const row = parseInt(cell.dataset.row);
    const col = parseInt(cell.dataset.col);
    const value = cell.textContent;
    
    // Highlight cells in the same row, column, and box
    highlightRelatedCells(row, col, value);
}

// Highlight cells related to the selected cell
function highlightRelatedCells(row, col, value) {
    const cells = document.querySelectorAll('.sudoku-cell');
    
    cells.forEach(cell => {
        const cellRow = parseInt(cell.dataset.row);
        const cellCol = parseInt(cell.dataset.col);
        
        // Highlight cells in the same row, column, or box
        if (cellRow === row || cellCol === col || 
            (Math.floor(cellRow / 3) === Math.floor(row / 3) && 
             Math.floor(cellCol / 3) === Math.floor(col / 3))) {
            cell.classList.add('highlighted');
        }
        
        // Highlight cells with the same number
        if (cell.textContent === value && value !== '') {
            cell.classList.add('same-number');
        }
    });
}

// Input a number into the selected cell
function inputNumber(number) {
    if (!selectedCell) return;
    
    const row = parseInt(selectedCell.dataset.row);
    const col = parseInt(selectedCell.dataset.col);
    
    // Update the cell and puzzle state
    selectedCell.textContent = number;
    currentPuzzle[row][col] = number;
    
    // Validate the number
    validateMove(row, col, number);
    
    // Check if the puzzle is complete
    checkPuzzleCompletion();
    
    // Highlight related cells
    selectCell(selectedCell);
}

// Erase the number in the selected cell
function eraseNumber() {
    if (!selectedCell) return;
    
    const row = parseInt(selectedCell.dataset.row);
    const col = parseInt(selectedCell.dataset.col);
    
    // Update the cell and puzzle state
    selectedCell.textContent = '';
    currentPuzzle[row][col] = 0;
    
    // Remove validation classes
    selectedCell.classList.remove('valid', 'invalid');
    
    // Highlight related cells
    selectCell(selectedCell);
}

// Validate a move by checking if it conflicts with any existing numbers
function validateMove(row, col, number) {
    const isValid = isValidMove(row, col, number);
    const cell = document.querySelector(`.sudoku-cell[data-row="${row}"][data-col="${col}"]`);
    
    // Update the cell's appearance based on validity
    cell.classList.remove('valid', 'invalid');
    cell.classList.add(isValid ? 'valid' : 'invalid');
}

// Check if a number is valid in the current position
function isValidMove(row, col, number) {
    // Check row
    for (let i = 0; i < 9; i++) {
        if (i !== col && currentPuzzle[row][i] === number) {
            return false;
        }
    }
    
    // Check column
    for (let i = 0; i < 9; i++) {
        if (i !== row && currentPuzzle[i][col] === number) {
            return false;
        }
    }
    
    // Check 3x3 box
    const boxRow = Math.floor(row / 3) * 3;
    const boxCol = Math.floor(col / 3) * 3;
    
    for (let i = 0; i < 3; i++) {
        for (let j = 0; j < 3; j++) {
            const r = boxRow + i;
            const c = boxCol + j;
            if ((r !== row || c !== col) && currentPuzzle[r][c] === number) {
                return false;
            }
        }
    }
    
    return true;
}

// Get an AI-powered hint from the server
function getAIHint() {
    // Show a loading indicator in the hint display
    showHintDisplay();
    hintMessage.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Generating AI hint...';
    hintTechnique.textContent = '';
    
    fetch('/get_hint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            original_puzzle: originalPuzzle,
            puzzle: currentPuzzle,
            solution: currentSolution,
            difficulty: currentDifficulty,
            hint_type: 'ai'
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.hint_type === 'complete') {
            hintMessage.textContent = data.message;
            hintTechnique.textContent = '';
            return;
        }
        
        // Display the AI hint message
        hintMessage.textContent = data.message;
        
        // Show the technique used (if available)
        if (data.technique) {
            hintTechnique.textContent = `Technique: ${data.technique}`;
        } else {
            hintTechnique.textContent = '';
        }
        
        // If the hint includes row/col coordinates, highlight that cell
        if (data.row !== undefined && data.col !== undefined) {
            const cell = document.querySelector(`.sudoku-cell[data-row="${data.row}"][data-col="${data.col}"]`);
            if (cell) {
                // Highlight the cell
                cell.classList.add('hint');
                
                // Select the cell
                selectCell(cell);
                
                // Remove the hint class after 5 seconds
                setTimeout(() => {
                    cell.classList.remove('hint');
                }, 5000);
            }
        }
    })
    .catch(error => {
        console.error('Error getting AI hint:', error);
        hintMessage.textContent = "Sorry, couldn't generate a hint. Please try again.";
        hintTechnique.textContent = '';
    });
}

// Get a solution hint from the server (original hint behavior)
function getSolutionHint() {
    fetch('/get_hint', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            original_puzzle: originalPuzzle,
            puzzle: currentPuzzle,
            solution: currentSolution,
            difficulty: currentDifficulty,
            hint_type: 'solution'
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.hint_type === 'complete') {
            showHintDisplay();
            hintMessage.textContent = data.message;
            hintTechnique.textContent = '';
            return;
        }
        
        // Highlight the cell with the hint
        const cell = document.querySelector(`.sudoku-cell[data-row="${data.row}"][data-col="${data.col}"]`);
        cell.classList.add('hint');
        
        // Fill in the value
        cell.textContent = data.value;
        currentPuzzle[data.row][data.col] = data.value;
        
        // Select the cell
        selectCell(cell);
        
        // Show hint message
        showHintDisplay();
        hintMessage.textContent = data.message || `The correct number for this cell is ${data.value}.`;
        hintTechnique.textContent = '';
        
        // Check if the puzzle is complete
        checkPuzzleCompletion();
        
        // Remove the hint class after 3 seconds
        setTimeout(() => {
            cell.classList.remove('hint');
        }, 3000);
    })
    .catch(error => {
        console.error('Error getting solution hint:', error);
        showHintDisplay();
        hintMessage.textContent = "Sorry, couldn't generate a hint. Please try again.";
        hintTechnique.textContent = '';
    });
}

// Show the hint display panel
function showHintDisplay() {
    hintDisplay.classList.remove('d-none');
}

// Hide the hint display panel
function hideHintDisplay() {
    hintDisplay.classList.add('d-none');
}

// Check if the puzzle is valid and complete
function checkPuzzleCompletion() {
    fetch('/validate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            puzzle: currentPuzzle,
            solution: currentSolution
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.valid) {
            if (data.complete) {
                // Update the completed difficulty in the modal
                document.getElementById('completed-difficulty').textContent = capitalizeFirstLetter(currentDifficulty);
                
                // Create confetti celebration effect
                createConfetti();
                
                // Puzzle is complete and valid
                gameCompletedModal.show();
            } else {
                // Puzzle is valid but not complete
                showMessage('success', 'So far, so good! Keep going!');
            }
        } else {
            // Puzzle has errors
            showMessage('danger', 'There are some errors in your puzzle. Please check again.');
        }
    })
    .catch(error => console.error('Error validating puzzle:', error));
}

// Show a toast message
function showMessage(type, message) {
    // Create a toast element
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0 position-fixed bottom-0 end-0 m-3`;
    toast.setAttribute('role', 'alert');
    toast.setAttribute('aria-live', 'assertive');
    toast.setAttribute('aria-atomic', 'true');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
        </div>
    `;
    
    // Add to document
    document.body.appendChild(toast);
    
    // Initialize and show the toast
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();
    
    // Remove after it's hidden
    toast.addEventListener('hidden.bs.toast', function() {
        toast.remove();
    });
}

// Create confetti celebration effect
function createConfetti() {
    const colors = [
        'var(--smartsudo-primary)',
        'var(--smartsudo-secondary)',
        'var(--smartsudo-accent)',
        'var(--smartsudo-highlight)'
    ];
    
    // Create 50 confetti particles
    for (let i = 0; i < 50; i++) {
        const confetti = document.createElement('div');
        confetti.className = 'confetti';
        confetti.style.left = `${Math.random() * 100}%`;
        confetti.style.backgroundColor = colors[Math.floor(Math.random() * colors.length)];
        confetti.style.width = `${5 + Math.random() * 10}px`;
        confetti.style.height = `${5 + Math.random() * 10}px`;
        confetti.style.opacity = Math.random();
        confetti.style.animationDuration = `${3 + Math.random() * 5}s`;
        confetti.style.animationDelay = `${Math.random() * 2}s`;
        
        document.querySelector('.modal-content').appendChild(confetti);
        
        // Remove the confetti after animation completes
        setTimeout(() => {
            confetti.remove();
        }, 8000);
    }
}

// Copy text to clipboard
function copyToClipboard(text) {
    // Create a temporary textarea element
    const textarea = document.createElement('textarea');
    textarea.value = text;
    textarea.setAttribute('readonly', '');
    textarea.style.position = 'absolute';
    textarea.style.left = '-9999px';
    document.body.appendChild(textarea);
    
    // Select and copy the text
    textarea.select();
    document.execCommand('copy');
    
    // Remove the temporary element
    document.body.removeChild(textarea);
}

// Set up event listeners for the game
function setupEventListeners() {
    // Cell selection event listener
    gameBoard.addEventListener('click', (event) => {
        if (event.target.classList.contains('sudoku-cell')) {
            selectCell(event.target);
        }
    });
    
    // Setup number pad listeners
    setupNumberPadListeners();
    
    // New game button event listener
    newGameButton.addEventListener('click', fetchNewPuzzle);
    
    // New game after win button event listener
    newGameAfterWinButton.addEventListener('click', () => {
        gameCompletedModal.hide();
        fetchNewPuzzle();
    });
    
    // Share result button event listener
    document.getElementById('shareResultBtn').addEventListener('click', () => {
        const difficulty = document.getElementById('completed-difficulty').textContent;
        const shareText = `I just solved a ${difficulty} level puzzle in SmartSudo! Can you beat me? 🧩`;
        
        // Check if Web Share API is available
        if (navigator.share) {
            navigator.share({
                title: 'SmartSudo Challenge',
                text: shareText,
                url: window.location.href,
            })
            .catch(error => {
                console.error('Error sharing:', error);
                // Fallback
                copyToClipboard(shareText + ' ' + window.location.href);
                showMessage('info', 'Share text copied to clipboard!');
            });
        } else {
            // Fallback for browsers that don't support the Web Share API
            copyToClipboard(shareText + ' ' + window.location.href);
            showMessage('info', 'Share text copied to clipboard!');
        }
    });
    
    // AI hint button event listener
    aiHintButton.addEventListener('click', (event) => {
        event.preventDefault();
        getAIHint();
    });
    
    // Solution hint button event listener
    solutionHintButton.addEventListener('click', (event) => {
        event.preventDefault();
        getSolutionHint();
    });
    
    // Check button event listener
    checkButton.addEventListener('click', checkPuzzleCompletion);
    
    // Difficulty options event listeners
    difficultyOptions.forEach(option => {
        option.addEventListener('click', (event) => {
            event.preventDefault();
            currentDifficulty = option.dataset.difficulty;
            currentDifficultyElement.textContent = capitalizeFirstLetter(currentDifficulty);
            fetchNewPuzzle();
        });
    });
    
    // Grid size options event listeners
    gridSizeOptions.forEach(option => {
        option.addEventListener('click', (event) => {
            event.preventDefault();
            const gridType = option.dataset.gridType;
            const gridSizeText = option.textContent;
            
            currentGridType = gridType;
            currentGridSizeElement.textContent = gridSizeText;
            
            // Update grid size based on type
            switch(gridType) {
                case '2x2':
                    currentGridSize = 4;
                    currentBoxSize = 2;
                    break;
                case '3x3':
                    currentGridSize = 9;
                    currentBoxSize = 3;
                    break;
                case '4x4':
                    currentGridSize = 16;
                    currentBoxSize = 4;
                    break;
            }
            
            fetchNewPuzzle();
        });
    });
    
    // Keyboard input event listener
    document.addEventListener('keydown', (event) => {
        if (!selectedCell) return;
        
        const keyNumber = parseInt(event.key);
        if (keyNumber >= 1 && keyNumber <= currentGridSize) {
            inputNumber(keyNumber);
        } else if (event.key === 'Backspace' || event.key === 'Delete') {
            eraseNumber();
        } else if (event.key === 'ArrowUp') {
            moveSelection(0, -1);
        } else if (event.key === 'ArrowDown') {
            moveSelection(0, 1);
        } else if (event.key === 'ArrowLeft') {
            moveSelection(-1, 0);
        } else if (event.key === 'ArrowRight') {
            moveSelection(1, 0);
        }
    });
}

// Move the selection in the specified direction
function moveSelection(dx, dy) {
    if (!selectedCell) return;
    
    const row = parseInt(selectedCell.dataset.row);
    const col = parseInt(selectedCell.dataset.col);
    const newRow = Math.max(0, Math.min(currentGridSize - 1, row + dy));
    const newCol = Math.max(0, Math.min(currentGridSize - 1, col + dx));
    
    if (newRow === row && newCol === col) return;
    
    const newCell = document.querySelector(`.sudoku-cell[data-row="${newRow}"][data-col="${newCol}"]`);
    
    if (newCell) {
        selectCell(newCell);
    }
}

// Helper function to capitalize the first letter of a string
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
