import random
import copy

class SudokuGenerator:
    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = None
    
    def generate_puzzle(self, difficulty='medium'):
        """Generate a new Sudoku puzzle with the given difficulty."""
        
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        
        
        self._fill_grid()
        
        
        self.solution = copy.deepcopy(self.grid)
        
        # Remove cells based on difficulty
        self._remove_cells(difficulty)
        
        return self.grid, self.solution
    
    def _fill_grid(self):
        """Fill the grid with a valid Sudoku solution."""
        # valid sequence 1-9
        nums = list(range(1, 10))
        random.shuffle(nums)
        
        # Fill using backtracking
        self._fill_grid_recursive(0, 0, nums)
    
    def _fill_grid_recursive(self, row, col, nums):
        """Recursively fill the grid using backtracking."""
        # If we're at end of grid, we done
        if row == 9:
            return True
        
        # If already filled, move to next cell
        if self.grid[row][col] != 0:
            if col == 8:
                return self._fill_grid_recursive(row + 1, 0, nums)
            return self._fill_grid_recursive(row, col + 1, nums)
        
        # Try each 1-9
        temp_nums = nums.copy()
        random.shuffle(temp_nums)
        
        for num in temp_nums:
            if self._is_valid(row, col, num):
                self.grid[row][col] = num
                
                # Move to next cell
                next_row, next_col = (row, col + 1) if col < 8 else (row + 1, 0)
                if self._fill_grid_recursive(next_row, next_col, nums):
                    return True
                
                # need to backtrack
                self.grid[row][col] = 0
        
        return False
    
    def _is_valid(self, row, col, num):
        """Check if a number is valid in the given position."""
        
        for i in range(9):
            if self.grid[row][i] == num:
                return False
        
        
        for i in range(9):
            if self.grid[i][col] == num:
                return False
        
        
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for i in range(box_row, box_row + 3):
            for j in range(box_col, box_col + 3):
                if self.grid[i][j] == num:
                    return False
        
        return True
    
    def _remove_cells(self, difficulty):
        """Remove cells based on difficulty."""
        
        difficulty_levels = {
            'easy': 35,       # filled 46 cells 
            'medium': 45,     # 36 cells 
            'hard': 55,       # 26 cells 
            'expert': 60      # 21 cells 
        }
        
        
        cells_to_remove = difficulty_levels.get(difficulty, 45)
        
        
        positions = [(i, j) for i in range(9) for j in range(9)]
        random.shuffle(positions)
        
        
        for i, j in positions[:cells_to_remove]:
            self.grid[i][j] = 0
