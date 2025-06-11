import random
import copy

class SudokuGenerator:
    def __init__(self, n=3):
        self.n = n  # Size of each box (default 3 for 9x9 grid)
        self.size = n * n  # Total grid size (default 9)
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        self.solution = None
    
    def generate_puzzle(self, difficulty='medium'):
        """Generate a new Sudoku puzzle with the given difficulty."""
        # Reset the grid
        self.grid = [[0 for _ in range(self.size)] for _ in range(self.size)]
        
        # Generate a solved Sudoku grid
        self._fill_grid()
        
        # Store the solution
        self.solution = copy.deepcopy(self.grid)
        
        # Remove cells based on difficulty
        self._remove_cells(difficulty)
        
        return self.grid, self.solution
    
    def _fill_grid(self):
        """Fill the grid with a valid Sudoku solution."""
        # Generate a valid sequence 1 to size
        nums = list(range(1, self.size + 1))
        random.shuffle(nums)
        
        # Fill the grid using backtracking
        self._fill_grid_recursive(0, 0, nums)
    
    def _fill_grid_recursive(self, row, col, nums):
        """Recursively fill the grid using backtracking."""
        # If we're at the end of the grid, we're done
        if row == self.size:
            return True
        
        # If this cell is already filled, move to the next cell
        if self.grid[row][col] != 0:
            if col == self.size - 1:
                return self._fill_grid_recursive(row + 1, 0, nums)
            return self._fill_grid_recursive(row, col + 1, nums)
        
        # Try each number 1 to size
        temp_nums = nums.copy()
        random.shuffle(temp_nums)
        
        for num in temp_nums:
            if self._is_valid(row, col, num):
                self.grid[row][col] = num
                
                # Move to the next cell
                next_row, next_col = (row, col + 1) if col < self.size - 1 else (row + 1, 0)
                if self._fill_grid_recursive(next_row, next_col, nums):
                    return True
                
                # If we reach here, we need to backtrack
                self.grid[row][col] = 0
        
        return False
    
    def _is_valid(self, row, col, num):
        """Check if a number is valid in the given position."""
        # Check row
        for i in range(self.size):
            if self.grid[row][i] == num:
                return False
        
        # Check column
        for i in range(self.size):
            if self.grid[i][col] == num:
                return False
        
        # Check nxn box
        box_row, box_col = self.n * (row // self.n), self.n * (col // self.n)
        for i in range(box_row, box_row + self.n):
            for j in range(box_col, box_col + self.n):
                if self.grid[i][j] == num:
                    return False
        
        return True
    
    def _remove_cells(self, difficulty):
        """Remove cells based on difficulty."""
        # Calculate percentage of cells to remove based on grid size
        total_cells = self.size * self.size
        
        # Define difficulty levels as percentages
        difficulty_percentages = {
            'easy': 0.4,      # Remove 40% of cells
            'medium': 0.55,   # Remove 55% of cells
            'hard': 0.65,     # Remove 65% of cells
            'expert': 0.75    # Remove 75% of cells
        }
        
        # Get the percentage to remove
        remove_percentage = difficulty_percentages.get(difficulty, 0.55)
        cells_to_remove = int(total_cells * remove_percentage)
        
        # Create a list of all positions
        positions = [(i, j) for i in range(self.size) for j in range(self.size)]
        random.shuffle(positions)
        
        # Remove cells
        for i, j in positions[:cells_to_remove]:
            self.grid[i][j] = 0
