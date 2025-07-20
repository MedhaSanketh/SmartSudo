import os
import random

client = None

def initialize_openai():
    
    global client
    try:
        
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
    try:
        
        if client is None:
            initialize_openai()
        
        
        empty_cells = []
        for i in range(9):
            for j in range(9):
                if current_state[i][j] == 0:
                    empty_cells.append((i, j))
        
        if not empty_cells:
            return {"hint_type": "complete", "message": "The puzzle is already complete!"}
        
        
        for row in range(9):
            for col in range(9):
                if current_state[row][col] == 0:
                    valid_nums = get_valid_numbers(current_state, row, col)
                    if len(valid_nums) == 1:
                        
                        return {
                            'hint_type': 'straightforward',
                            'row': row,
                            'col': col,
                            'number': valid_nums[0],
                            'message': f"Cell at row {row+1}, column {col+1} can only be {valid_nums[0]} based on current constraints."
                        }
        
        
        best_cell = None
        min_options = 10
        
        for row in range(9):
            for col in range(9):
                if current_state[row][col] == 0:
                    valid_nums = get_valid_numbers(current_state, row, col)
                    if 1 < len(valid_nums) < min_options:
                        min_options = len(valid_nums)
                        best_cell = (row, col, valid_nums)
        
        if best_cell:
            row, col, valid_nums = best_cell
            
            
            if client:
                puzzle_str = format_puzzle_for_ai(current_state)
                hint_context = {
                    "row": row + 1,
                    "col": col + 1,
                    "valid_options": valid_nums,
                    "row_values": [num for num in current_state[row] if num != 0],
                    "col_values": [current_state[i][col] for i in range(9) if current_state[i][col] != 0],
                    "box_values": get_box_values(current_state, row, col)
                }
                return generate_ai_hint(puzzle_str, hint_context, difficulty, valid_nums)
            else:
                
                return generate_basic_hint(row, col, valid_nums)
        
        
        row, col = random.choice(empty_cells)
        valid_nums = get_valid_numbers(current_state, row, col)
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
    
    for i in range(9):
        if grid[row][i] == num:
            return False
    
    
    for i in range(9):
        if grid[i][col] == num:
            return False
    

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
        if not client:
            return generate_basic_hint(hint_context["row"] - 1, hint_context["col"] - 1, valid_nums)
            
       
        hint_level = "subtle" if difficulty in ["hard", "expert"] else "medium"
        
        
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

        
        response = client.chat.completions.create(
            model="gpt-4o",  
            messages=[
                {"role": "system", "content": "You are a Sudoku expert assistant. Provide hints rather than solutions."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=200
        )
        
        
        response_content = response.choices[0].message.content
        
        
        import json
        if response_content is not None:
            hint_data = json.loads(str(response_content))
        else:
            hint_data = {"hint_type": "basic", "message": "Try examining the rows, columns, and boxes for this cell."}
        
        
        hint_data["row"] = hint_context["row"] - 1  
        hint_data["col"] = hint_context["col"] - 1
        
        return hint_data
        
    except Exception as e:
        
        return generate_basic_hint(hint_context["row"] - 1, hint_context["col"] - 1, valid_nums)