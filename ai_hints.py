"""
AI-powered hints for Sudoku puzzles using OpenAI.
This module provides intelligent hints without solving the entire puzzle.
"""
import os
from openai import OpenAI

# Try to get API key from environment variable first, then from config file
try:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        from config import OPENAI_API_KEY
        api_key = OPENAI_API_KEY
except ImportError:
    api_key = os.environ.get("OPENAI_API_KEY")

# Initialize OpenAI client
client = OpenAI(api_key=api_key)

def generate_hint(puzzle, current_state, difficulty):
    """
    Generate an AI-powered hint for the current Sudoku puzzle.
    
    Args:
        puzzle: The original puzzle
        current_state: The current state of the puzzle
        difficulty: The difficulty level of the puzzle
    
    Returns:
        A hint object with row, col, and explanation
    """
    # Find empty cells
    empty_cells = []
    for i in range(9):
        for j in range(9):
            if current_state[i][j] == 0:
                empty_cells.append((i, j))
    
    if not empty_cells:
        return {"hint_type": "complete", "message": "The puzzle is already complete!"}
    
    # Pick a random empty cell for the hint
    import random
    row, col = random.choice(empty_cells)
    
    # Format the puzzle state for OpenAI
    puzzle_str = format_puzzle_for_ai(current_state)
    
    # First, check if there's only one possible value for this cell
    valid_nums = get_valid_numbers(current_state, row, col)
    
    if len(valid_nums) == 1:
        # If there's only one valid number, provide a basic hint
        value = valid_nums[0]
        return {
            "hint_type": "straightforward",
            "row": row,
            "col": col,
            "value": value,
            "message": f"In row {row+1}, column {col+1}, only the number {value} is possible."
        }
    
    # If there are multiple valid numbers, use AI to provide a more detailed hint
    hint_context = {
        "row": row + 1,  # Convert to 1-indexed for readability
        "col": col + 1,
        "valid_options": valid_nums,
        "row_values": [num for num in current_state[row] if num != 0],
        "col_values": [current_state[i][col] for i in range(9) if current_state[i][col] != 0],
        "box_values": get_box_values(current_state, row, col)
    }
    
    # Generate an AI hint
    return generate_ai_hint(puzzle_str, hint_context, difficulty, valid_nums)

def get_valid_numbers(grid, row, col):
    """Get all valid numbers for a cell."""
    if grid[row][col] != 0:
        return []
        
    valid = []
    for num in range(1, 10):
        if is_valid_move(grid, row, col, num):
            valid.append(num)
    return valid

def is_valid_move(grid, row, col, num):
    """Check if a number is valid in the given position."""
    # Check row
    for i in range(9):
        if grid[row][i] == num:
            return False
    
    # Check column
    for i in range(9):
        if grid[i][col] == num:
            return False
    
    # Check 3x3 box
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if grid[i][j] == num:
                return False
    
    return True

def get_box_values(grid, row, col):
    """Get values in the 3x3 box containing the cell."""
    box_row, box_col = 3 * (row // 3), 3 * (col // 3)
    values = []
    for i in range(box_row, box_row + 3):
        for j in range(box_col, box_col + 3):
            if grid[i][j] != 0:
                values.append(grid[i][j])
    return values

def format_puzzle_for_ai(grid):
    """Format the Sudoku grid as a string for the AI."""
    result = ""
    for i in range(9):
        if i > 0 and i % 3 == 0:
            result += "------+-------+------\n"
        for j in range(9):
            if j > 0 and j % 3 == 0:
                result += "| "
            cell = "." if grid[i][j] == 0 else str(grid[i][j])
            result += cell + " "
        result += "\n"
    return result

def generate_ai_hint(puzzle_str, hint_context, difficulty, valid_nums):
    """Generate a hint using OpenAI's API."""
    try:
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
        return {
            "hint_type": "basic",
            "row": hint_context["row"] - 1,
            "col": hint_context["col"] - 1,
            "message": f"Try looking at row {hint_context['row']}, column {hint_context['col']}. What numbers are still possible here?",
            "valid_options": valid_nums
        }