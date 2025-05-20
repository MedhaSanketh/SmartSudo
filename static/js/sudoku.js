// Global variables to store the game state
let currentPuzzle = [];
let originalPuzzle = []; // Store the original puzzle for AI hints
let currentSolution = [];
let selectedCell = null;
let currentDifficulty = 'medium';
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

// Create the 9x9 Sudoku grid
function createGameBoard() {
    gameBoard.innerHTML = '';
    
    for (let row = 0; row < 9; row++) {
        for (let col = 0; col < 9; col++) {
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
    fetch(`/new_puzzle?difficulty=${currentDifficulty}`)
        .then(response => response.json())
        .then(data => {
            currentPuzzle = data.puzzle;
            // Make a deep copy of the original puzzle for AI hints
            originalPuzzle = JSON.parse(JSON.stringify(data.puzzle));
            currentSolution = data.solution;
            currentDifficulty = data.difficulty;
            renderPuzzle();
            fixedCells = [];
            
            // Mark initial cells as fixed
            for (let row = 0; row < 9; row++) {
                for (let col = 0; col < 9; col++) {
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
                // Puzzle is complete and valid
                gameCompletedModal.show();
            } else {
                // Puzzle is valid but not complete
                alert('So far, so good! Keep going!');
            }
        } else {
            // Puzzle has errors
            alert('There are some errors in your puzzle. Please check again.');
        }
    })
    .catch(error => console.error('Error validating puzzle:', error));
}

// Set up event listeners for the game
function setupEventListeners() {
    // Cell selection event listener
    gameBoard.addEventListener('click', (event) => {
        if (event.target.classList.contains('sudoku-cell')) {
            selectCell(event.target);
        }
    });
    
    // Number buttons event listeners
    numberButtons.forEach(button => {
        button.addEventListener('click', () => {
            const number = parseInt(button.dataset.number);
            inputNumber(number);
        });
    });
    
    // Erase button event listener
    eraseButton.addEventListener('click', eraseNumber);
    
    // New game button event listener
    newGameButton.addEventListener('click', fetchNewPuzzle);
    
    // New game after win button event listener
    newGameAfterWinButton.addEventListener('click', () => {
        gameCompletedModal.hide();
        fetchNewPuzzle();
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
    
    // Keyboard input event listener
    document.addEventListener('keydown', (event) => {
        if (!selectedCell) return;
        
        if (event.key >= '1' && event.key <= '9') {
            inputNumber(parseInt(event.key));
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
    const newRow = Math.max(0, Math.min(8, row + dy));
    const newCol = Math.max(0, Math.min(8, col + dx));
    
    if (newRow === row && newCol === col) return;
    
    const newCell = document.querySelector(`.sudoku-cell[data-row="${newRow}"][data-col="${newCol}"]`);
    
    if (newCell && !newCell.classList.contains('fixed')) {
        selectCell(newCell);
    } else {
        // If the new cell is fixed, try to move in the same direction again
        moveSelection(dx, dy);
    }
}

// Helper function to capitalize the first letter of a string
function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
}
