import random
import copy

class SudokuGenerator:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = None
    
    def generate_puzzle(self, difficulty='medium'):
        """Generate a new Sudoku puzzle with the given difficulty."""
        # Reset the grid
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        
        # Generate a solved Sudoku grid
        self._fill_grid()
        
        # Store the solution
        self.solution = copy.deepcopy(self.grid)
        
        # Remove cells based on difficulty
        self._remove_cells(difficulty)
        
        return self.grid, self.solution
    
    def _fill_grid(self):
        """Fill the grid with a valid Sudoku solution."""
        # Generate a valid sequence 1-9
        nums = list(range(1, 10))
        random.shuffle(nums)
        
        # Fill the grid using backtracking
        self._fill_grid_recursive(0, 0, nums)
    
    def _fill_grid_recursive(self, row, col, nums):
        """Recursively fill the grid using backtracking."""
        # If we're at the end of the grid, we're done
        if row == 9:
            return True
        
        # If this cell is already filled, move to the next cell
        if self.grid[row][col] != 0:
            if col == 8:
                return self._fill_grid_recursive(row + 1, 0, nums)
            return self._fill_grid_recursive(row, col + 1, nums)
        
        # Try each number 1-9
        temp_nums = nums.copy()
        random.shuffle(temp_nums)
        
        for num in temp_nums:
            if self._is_valid(row, col, num):
                self.grid[row][col] = num
                
                # Move to the next cell
                next_row, next_col = (row, col + 1) if col < 8 else (row + 1, 0)
                if self._fill_grid_recursive(next_row, next_col, nums):
                    return True
                
                # If we reach here, we need to backtrack
                self.grid[row][col] = 0
        
        return False
    
    def _is_valid(self, row, col, num):
        """Check if a number is valid in the given position."""
        # Check row
        for i in range(9):
            if self.grid[row][i] == num:
                return False
        
        # Check column
        for i in range(9):
            if self.grid[i][col] == num:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.grid[i][j] == num:
                    return False
        
        return True
    
    def _remove_cells(self, difficulty):
        """Remove cells based on difficulty."""
        # Define difficulty levels
        difficulty_levels = {
            'easy': 35,       # 46 cells filled
            'medium': 45,     # 36 cells filled
            'hard': 55,       # 26 cells filled
            'expert': 60      # 21 cells filled
        }
        
        # Get the number of cells to remove
        cells_to_remove = difficulty_levels.get(difficulty, 45)
        
        # Create a list of all positions
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        # Remove cells
        for i, j in positions[:cells_to_remove]:
            self.grid[i][j] = 0
