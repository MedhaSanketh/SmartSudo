import os
import logging
from flask import Flask, render_template, jsonify, request
from sudoku_generator import SudokuGenerator
from visualization import get_visualization_data
from ai_hints import generate_hint

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize the Sudoku generator (will be recreated based on user input)
sudoku_generator = None

@app.route('/')
def index():
    """Render the main Sudoku game page."""
    return render_template('index.html')

@app.route('/new_puzzle', methods=['GET'])
def new_puzzle():
    """Generate a new Sudoku puzzle with the requested difficulty."""
    difficulty = request.args.get('difficulty', 'medium')
    n = int(request.args.get('n', 3))  # Get box size, default 3
    
    # Create generator for the requested grid size
    generator = SudokuGenerator(n)
    grid, solution = generator.generate_puzzle(difficulty)
    
    return jsonify({
        'puzzle': grid,
        'solution': solution,
        'difficulty': difficulty,
        'n': n,
        'size': n * n
    })

@app.route('/get_hint', methods=['POST'])
def get_hint():
    """Provide an AI-powered hint for the current puzzle state."""
    data = request.json if request.json else {}
    puzzle = data.get('original_puzzle', [])
    current_state = data.get('puzzle', [])
    solution = data.get('solution', [])
    difficulty = data.get('difficulty', 'medium')
    hint_type = data.get('hint_type', 'ai')  # 'ai' or 'solution'
    n = data.get('n', 3)  # Get box size
    size = n * n
    
    if hint_type == 'solution':
        # Provide a direct solution hint (original behavior)
        for i in range(size):
            for j in range(size):
                if current_state[i][j] == 0 or current_state[i][j] != solution[i][j]:
                    return jsonify({
                        'hint_type': 'solution',
                        'row': i,
                        'col': j,
                        'value': solution[i][j],
                        'message': f"The correct number for this cell is {solution[i][j]}."
                    })
        
        # No hints needed, puzzle is complete
        return jsonify({'hint_type': 'complete', 'message': 'The puzzle is already complete!'})
    else:
        # Provide an AI-powered hint
        try:
            hint = generate_hint(puzzle, current_state, difficulty, n)
            return jsonify(hint)
        except Exception as e:
            logging.error(f"Error generating AI hint: {str(e)}")
            # Fallback to solution hint if AI fails
            return jsonify({
                'hint_type': 'error',
                'message': "Sorry, I couldn't generate a smart hint. Try again or use a solution hint."
            })

@app.route('/validate', methods=['POST'])
def validate():
    """Validate the current puzzle against the solution."""
    data = request.json if request.json else {}
    puzzle = data.get('puzzle', [])
    solution = data.get('solution', [])
    n = data.get('n', 3)
    size = n * n
    
    # Check if the puzzle matches the solution
    valid = all(puzzle[i][j] == solution[i][j] for i in range(size) for j in range(size) if puzzle[i][j] != 0)
    complete = all(puzzle[i][j] != 0 for i in range(size) for j in range(size))
    
    return jsonify({
        'valid': valid,
        'complete': complete
    })

@app.route('/visualize_backtracking', methods=['POST'])
def visualize_backtracking():
    """Generate backtracking visualization data for the current puzzle."""
    data = request.json if request.json else {}
    puzzle = data.get('puzzle', []) if data else []
    n = data.get('n', 3)
    
    try:
        # Get visualization data
        steps, decision_tree = get_visualization_data(puzzle, n)
        
        # Simplify and limit the data to avoid very large responses
        simplified_steps = []
        max_steps = 500  # Limit to a reasonable number of steps
        
        for i, step in enumerate(steps):
            if i >= max_steps:
                break
                
            simplified_steps.append({
                'grid': step['grid'],
                'message': step['message'],
                'row': step['row'],
                'col': step['col'],
                'value': step['value'],
                'is_decision': step['is_decision'],
                'is_backtrack': step['is_backtrack']
            })
        
        return jsonify({
            'steps': simplified_steps,
            'decision_tree': decision_tree[:max_steps] if len(decision_tree) > max_steps else decision_tree
        })
    except Exception as e:
        logging.error(f"Error generating visualization: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
