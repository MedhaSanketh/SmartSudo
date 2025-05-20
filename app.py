import os
import logging
from flask import Flask, render_template, jsonify, request
from sudoku_generator import SudokuGenerator

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize the Sudoku generator
sudoku_generator = SudokuGenerator()

@app.route('/')
def index():
    """Render the main Sudoku game page."""
    return render_template('index.html')

@app.route('/new_puzzle', methods=['GET'])
def new_puzzle():
    """Generate a new Sudoku puzzle with the requested difficulty."""
    difficulty = request.args.get('difficulty', 'medium')
    grid, solution = sudoku_generator.generate_puzzle(difficulty)
    return jsonify({
        'puzzle': grid,
        'solution': solution
    })

@app.route('/get_hint', methods=['POST'])
def get_hint():
    """Provide a hint for the current puzzle state."""
    data = request.json
    puzzle = data.get('puzzle', [])
    solution = data.get('solution', [])
    
    # Find an empty cell or incorrect value
    for i in range(9):
        for j in range(9):
            if puzzle[i][j] == 0 or puzzle[i][j] != solution[i][j]:
                return jsonify({
                    'row': i,
                    'col': j,
                    'value': solution[i][j]
                })
    
    # No hints needed, puzzle is complete
    return jsonify({'status': 'complete'})

@app.route('/validate', methods=['POST'])
def validate():
    """Validate the current puzzle against the solution."""
    data = request.json
    puzzle = data.get('puzzle', [])
    solution = data.get('solution', [])
    
    # Check if the puzzle matches the solution
    valid = all(puzzle[i][j] == solution[i][j] for i in range(9) for j in range(9) if puzzle[i][j] != 0)
    complete = all(puzzle[i][j] != 0 for i in range(9) for j in range(9))
    
    return jsonify({
        'valid': valid,
        'complete': complete
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
