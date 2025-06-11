"""
AI-powered hints for Sudoku puzzles using OpenAI.
This module provides intelligent hints without solving the entire puzzle.
"""
import os
import random

# Initialize OpenAI client only when API key is available
client = None

def initialize_openai():
    """Initialize OpenAI client if API key is available."""
    global client
    try:
        # Try to get API key from config file first
        try:
            from config import OPENAI_API_KEY
            api_key = OPENAI_API_KEY
        except ImportError:
            api_key = os.environ.get("OPENAI_API_KEY")
        
        if api_key and api_key != "your_openai_api_key_here":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            return True
        return False
    except Exception as e:
        print(f"OpenAI initialization failed: {e}")
        return False

def generate_hint(puzzle, current_state, difficulty, n=3):
    """
    Generate an AI-powered hint for the current Sudoku puzzle.
    
    Args:
        puzzle: The original puzzle
        current_state: The current state of the puzzle
        difficulty: The difficulty level of the puzzle
        n: Size of each box (default 3 for 9x9 grid)
    
    Returns:
        A hint object with row, col, and explanation
    """
    try:
        # Initialize OpenAI if not already done
        if client is None:
            initialize_openai()
        
        size = n * n
        
        # Find empty cells
        empty_cells = []
        for i in range(size):
            for j in range(size):
                if current_state[i][j] == 0:
                    empty_cells.append((i, j))
        
        if not empty_cells:
            return {"hint_type": "complete", "message": "The puzzle is already complete!"}
        
        # Find an empty cell that can be solved with current information
        for row in range(size):
            for col in range(size):
                if current_state[row][col] == 0:
                    valid_nums = get_valid_numbers(current_state, row, col, n)
                    if len(valid_nums) == 1:
                        # Found a cell with only one valid number
                        return {
                            'hint_type': 'straightforward',
                            'row': row,
                            'col': col,
                            'number': valid_nums[0],
                            'message': f"Cell at row {row+1}, column {col+1} can only be {valid_nums[0]} based on current constraints."
                        }
        
        # Pick a cell with few possibilities for hint
        best_cell = None
        min_options = size + 1
        
        for row in range(size):
            for col in range(size):
                if current_state[row][col] == 0:
                    valid_nums = get_valid_numbers(current_state, row, col, n)
                    if 1 < len(valid_nums) < min_options:
                        min_options = len(valid_nums)
                        best_cell = (row, col, valid_nums)
        
        if best_cell:
            row, col, valid_nums = best_cell
            
            # If OpenAI is available, use AI hint
            if client:
                puzzle_str = format_puzzle_for_ai(current_state, n)
                hint_context = {
                    "row": row + 1,
                    "col": col + 1,
                    "valid_options": valid_nums,
                    "row_values": [num for num in current_state[row] if num != 0],
                    "col_values": [current_state[i][col] for i in range(size) if current_state[i][col] != 0],
                    "box_values": get_box_values(current_state, row, col, n)
                }
                return generate_ai_hint(puzzle_str, hint_context, difficulty, valid_nums)
            else:
                # Fallback to basic hint
                return generate_basic_hint(row, col, valid_nums)
        
        # Default fallback hint
        row, col = random.choice(empty_cells)
        valid_nums = get_valid_numbers(current_state, row, col, n)
        return generate_basic_hint(row, col, valid_nums)
        
    except Exception as e:
        return {
            'hint_type': 'error',
            'message': f"Unable to generate hint: {str(e)}"
        }

def generate_basic_hint(row, col, valid_nums):
    """Generate a basic hint when OpenAI is not available."""
    techniques = [
        "Look for naked singles - cells with only one possible value",
        "Check for hidden singles - numbers that can only go in one place in a row, column, or box", 
        "Use elimination - cross out numbers that already appear in the same row, column, or box",
        "Look for pointing pairs - when a number can only appear in one row or column within a box"
    ]
    
    technique = random.choice(techniques)
    
    return {
        "hint_type": "basic",
        "row": row,
        "col": col,
        "message": f"For row {row+1}, column {col+1}: {technique}. You have {len(valid_nums)} possible numbers: {valid_nums}",
        "valid_options": valid_nums
    }

def get_valid_numbers(grid, row, col, n=3):
    """Get all valid numbers for a cell."""
    if grid[row][col] != 0:
        return []
    
    size = n * n
    valid = []
    for num in range(1, size + 1):
        if is_valid_move(grid, row, col, num, n):
            valid.append(num)
    return valid

def is_valid_move(grid, row, col, num, n=3):
    """Check if a number is valid in the given position."""
    size = n * n
    
    # Check row
    for i in range(size):
        if grid[row][i] == num:
            return False
    
    # Check column
    for i in range(size):
        if grid[i][col] == num:
            return False
    
    # Check nxn box
    box_row, box_col = n * (row // n), n * (col // n)
    for i in range(box_row, box_row + n):
        for j in range(box_col, box_col + n):
            if grid[i][j] == num:
                return False
    
    return True

def get_box_values(grid, row, col, n=3):
    """Get values in the nxn box containing the cell."""
    box_row, box_col = n * (row // n), n * (col // n)
    values = []
    for i in range(box_row, box_row + n):
        for j in range(box_col, box_col + n):
            if grid[i][j] != 0:
                values.append(grid[i][j])
    return values

def format_puzzle_for_ai(grid, n=3):
    """Format the Sudoku grid as a string for the AI."""
    size = n * n
    result = ""
    for i in range(size):
        if i > 0 and i % n == 0:
            result += "-" * (size * 2 + n - 1) + "\n"
        for j in range(size):
            if j > 0 and j % n == 0:
                result += "| "
            cell = "." if grid[i][j] == 0 else str(grid[i][j])
            result += cell + " "
        result += "\n"
    return result

def generate_ai_hint(puzzle_str, hint_context, difficulty, valid_nums):
    """Generate a hint using OpenAI's API."""
    try:
        if not client:
            return generate_basic_hint(hint_context["row"] - 1, hint_context["col"] - 1, valid_nums)
            
        # Adjust the hint complexity based on difficulty
        hint_level = "subtle" if difficulty in ["hard", "expert"] else "medium"
        
        # Create a prompt for the AI
        prompt = f"""You are a Sudoku expert helping a player. Here's the current state of their Sudoku puzzle:

{puzzle_str}

I want you to provide a {hint_level} hint for the cell at row {hint_context['row']}, column {hint_context['col']}.

The valid options for this cell are: {hint_context['valid_options']}
Values already in this row: {hint_context['row_values']}
Values already in this column: {hint_context['col_values']}
Values already in this 3x3 box: {hint_context['box_values']}

Give a short, helpful hint that guides the player without directly solving it for them.
The hint should help them understand the Sudoku logic that applies here.

Return your response in the following JSON format:
{{"hint_type": "ai", "message": "your hint here", "technique": "the name of the technique"}}"""

        # Call the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            messages=[
                {"role": "system", "content": "You are a Sudoku expert assistant. Provide hints rather than solutions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        
        # Extract the hint from the response
        response_content = response.choices[0].message.content
        
        # Parse the JSON response
        import json
        if response_content is not None:
            hint_data = json.loads(str(response_content))
        else:
            hint_data = {"hint_type": "basic", "message": "Try examining the rows, columns, and boxes for this cell."}
        
        # Add the cell location to the hint
        hint_data["row"] = hint_context["row"] - 1  # Convert back to 0-indexed
        hint_data["col"] = hint_context["col"] - 1
        
        return hint_data
        
    except Exception as e:
        # Fallback to a simpler hint if the AI fails
        return generate_basic_hint(hint_context["row"] - 1, hint_context["col"] - 1, valid_nums)