import os
import logging
from flask import Flask, render_template, jsonify, request
from sudoku_generator import SudokuGenerator
from visualization import get_visualization_data
from advanced_solver import AdvancedSudokuSolver, compare_algorithms
from ai_hints import generate_hint
from variable_sudoku import create_variable_puzzle, VariableSudokuSolver

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

@app.route('/new_puzzle', methods=['GET', 'POST'])
def new_puzzle():
    """Generate a new Sudoku puzzle with the requested difficulty and grid size."""
    if request.method == 'GET':
        difficulty = request.args.get('difficulty', 'medium')
        grid_type = request.args.get('grid_type', '3x3')
    else:
        data = request.json if request.json else {}
        difficulty = data.get('difficulty', 'medium')
        grid_type = data.get('grid_type', '3x3')
    
    if grid_type == '3x3':
        # Use original generator for 9x9 puzzles
        generator = SudokuGenerator()
        result = generator.generate_puzzle(difficulty)
        puzzle_data = {
            'puzzle': result['puzzle'],
            'solution': result['solution'],
            'grid_size': 9,
            'box_size': 3
        }
    else:
        # Use variable generator for other sizes
        puzzle_data = create_variable_puzzle(grid_type, difficulty)
    
    return jsonify({
        'puzzle': puzzle_data['puzzle'],
        'solution': puzzle_data['solution'],
        'difficulty': difficulty,
        'grid_type': grid_type,
        'grid_size': puzzle_data['grid_size'],
        'box_size': puzzle_data['box_size']
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
    
    if hint_type == 'solution':
        # Provide a direct solution hint (original behavior)
        for i in range(9):
            for j in range(9):
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
            hint = generate_hint(puzzle, current_state, difficulty)
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
    
    # Check if the puzzle matches the solution
    valid = all(puzzle[i][j] == solution[i][j] for i in range(9) for j in range(9) if puzzle[i][j] != 0)
    complete = all(puzzle[i][j] != 0 for i in range(9) for j in range(9))
    
    return jsonify({
        'valid': valid,
        'complete': complete
    })

@app.route('/visualize_backtracking', methods=['POST'])
def visualize_backtracking():
    """Generate backtracking visualization data for the current puzzle."""
    data = request.json if request.json else {}
    puzzle = data.get('puzzle', []) if data else []
    
    try:
        # Get visualization data
        steps, decision_tree = get_visualization_data(puzzle)
        
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

@app.route('/advanced')
def advanced():
    """Render the advanced algorithm comparison page."""
    return render_template('advanced.html')

@app.route('/solve_advanced', methods=['POST'])
def solve_advanced():
    """Solve puzzle using MRV+LCV heuristics and return results."""
    try:
        data = request.json if request.json else {}
        puzzle = data.get('puzzle', [])
        grid_size = data.get('grid_size', 9)
        
        if not puzzle:
            return jsonify({'error': 'No puzzle provided'}), 400
        
        if grid_size == 9:
            advanced_solver = AdvancedSudokuSolver()
        else:
            advanced_solver = VariableSudokuSolver(grid_size)
        
        result = advanced_solver.solve_with_heuristics(puzzle)
        
        return jsonify(result)
        
    except Exception as e:
        logging.error(f"Error in solve_advanced: {str(e)}")
        return jsonify({'error': 'Failed to solve puzzle'}), 500

@app.route('/compare_algorithms', methods=['POST'])
def compare_algorithms_route():
    """Compare basic backtracking vs MRV+LCV algorithms."""
    try:
        data = request.json if request.json else {}
        puzzle = data.get('puzzle', [])
        
        if not puzzle:
            return jsonify({'error': 'No puzzle provided'}), 400
        
        comparison = compare_algorithms(puzzle)
        return jsonify(comparison)
        
    except Exception as e:
        logging.error(f"Error in compare_algorithms: {str(e)}")
        return jsonify({'error': 'Failed to compare algorithms'}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
