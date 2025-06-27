"""
Variable-size Sudoku generator and solver.
Supports 2x2 (4x4 grid), 3x3 (9x9 grid), and 4x4 (16x16 grid) Sudoku variants.
"""
import random
import time
from math import sqrt

class VariableSudokuGenerator:
    def __init__(self, grid_size=9):
        """
        Initialize generator for variable grid sizes.
        grid_size: 4 (2x2), 9 (3x3), or 16 (4x4)
        """
        self.grid_size = grid_size
        self.box_size = int(sqrt(grid_size))
        
    def generate_puzzle(self, difficulty='medium'):
        """Generate a puzzle for the specified grid size."""
        # Generate a complete solution first
        solution = self._generate_complete_grid()
        
        # Create puzzle by removing cells based on difficulty
        puzzle = [row[:] for row in solution]  # Deep copy
        self._remove_cells(puzzle, difficulty)
        
        return {
            'puzzle': puzzle,
            'solution': solution,
            'grid_size': self.grid_size,
            'box_size': self.box_size
        }
    
    def _generate_complete_grid(self):
        """Generate a complete valid Sudoku grid."""
        grid = [[0] * self.grid_size for _ in range(self.grid_size)]
        
        if self._solve_recursive(grid):
            return grid
        else:
            # Fallback: try again
            return self._generate_complete_grid()
    
    def _solve_recursive(self, grid):
        """Solve the grid using backtracking with randomization."""
        empty_cell = self._find_empty_cell(grid)
        if not empty_cell:
            return True  # Grid is complete
        
        row, col = empty_cell
        
        # Try numbers in random order for variety
        numbers = list(range(1, self.grid_size + 1))
        random.shuffle(numbers)
        
        for num in numbers:
            if self._is_valid_move(grid, row, col, num):
                grid[row][col] = num
                
                if self._solve_recursive(grid):
                    return True
                
                grid[row][col] = 0  # Backtrack
        
        return False
    
    def _find_empty_cell(self, grid):
        """Find the first empty cell in the grid."""
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if grid[row][col] == 0:
                    return (row, col)
        return None
    
    def _is_valid_move(self, grid, row, col, num):
        """Check if placing num at (row, col) is valid."""
        # Check row
        for c in range(self.grid_size):
            if grid[row][c] == num:
                return False
        
        # Check column
        for r in range(self.grid_size):
            if grid[r][col] == num:
                return False
        
        # Check box
        box_row = (row // self.box_size) * self.box_size
        box_col = (col // self.box_size) * self.box_size
        
        for r in range(box_row, box_row + self.box_size):
            for c in range(box_col, box_col + self.box_size):
                if grid[r][c] == num:
                    return False
        
        return True
    
    def _remove_cells(self, grid, difficulty):
        """Remove cells based on difficulty level."""
        total_cells = self.grid_size * self.grid_size
        
        if self.grid_size == 4:  # 2x2 Sudoku
            removal_ratios = {
                'easy': 0.3,    # Remove 30% (5 cells)
                'medium': 0.4,  # Remove 40% (6-7 cells)
                'hard': 0.5,    # Remove 50% (8 cells)
                'expert': 0.6   # Remove 60% (9-10 cells)
            }
        elif self.grid_size == 9:  # 3x3 Sudoku
            removal_ratios = {
                'easy': 0.45,   # Remove 45% (36 cells)
                'medium': 0.55, # Remove 55% (45 cells)
                'hard': 0.65,   # Remove 65% (53 cells)
                'expert': 0.75  # Remove 75% (61 cells)
            }
        else:  # 4x4 Sudoku (16x16 grid)
            removal_ratios = {
                'easy': 0.4,    # Remove 40% (102 cells)
                'medium': 0.5,  # Remove 50% (128 cells)
                'hard': 0.6,    # Remove 60% (154 cells)
                'expert': 0.7   # Remove 70% (179 cells)
            }
        
        cells_to_remove = int(total_cells * removal_ratios.get(difficulty, 0.5))
        
        # Get all cell positions
        all_positions = [(r, c) for r in range(self.grid_size) for c in range(self.grid_size)]
        random.shuffle(all_positions)
        
        # Remove cells
        removed = 0
        for row, col in all_positions:
            if removed >= cells_to_remove:
                break
            
            # Temporarily remove the cell
            original = grid[row][col]
            grid[row][col] = 0
            
            # Check if puzzle still has unique solution (simplified check)
            if self._has_unique_solution_simple(grid):
                removed += 1
            else:
                # Restore the cell if removing it makes puzzle invalid
                grid[row][col] = original
    
    def _has_unique_solution_simple(self, grid):
        """Simplified check for unique solution (basic validation)."""
        # For now, just ensure the puzzle is still solvable
        # A more sophisticated implementation would count all possible solutions
        test_grid = [row[:] for row in grid]
        return self._solve_recursive(test_grid)

class VariableSudokuSolver:
    def __init__(self, grid_size=9):
        self.grid_size = grid_size
        self.box_size = int(sqrt(grid_size))
        self.backtrack_count = 0
        self.solving_steps = []
        
    def solve_with_heuristics(self, puzzle):
        """Solve using MRV and LCV heuristics for variable grid sizes."""
        self.backtrack_count = 0
        self.solving_steps = []
        start_time = time.time()
        
        # Create working copy
        grid = [row[:] for row in puzzle]
        
        success = self._solve_mrv_lcv(grid)
        solving_time = time.time() - start_time
        
        return {
            'solved': success,
            'grid': grid if success else puzzle,
            'stats': {
                'backtrack_count': self.backtrack_count,
                'solving_time': solving_time,
                'steps': len(self.solving_steps),
                'grid_size': self.grid_size
            },
            'steps': self.solving_steps
        }
    
    def _solve_mrv_lcv(self, grid):
        """Recursive solver using MRV and LCV heuristics."""
        cell = self._select_cell_mrv(grid)
        
        if cell is None:
            return True  # Solved
        
        row, col = cell
        possible_values = self._get_values_lcv(grid, row, col)
        
        for value in possible_values:
            if self._is_valid_move(grid, row, col, value):
                grid[row][col] = value
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'value': value,
                    'action': 'place'
                })
                
                if self._solve_mrv_lcv(grid):
                    return True
                
                grid[row][col] = 0
                self.backtrack_count += 1
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'value': value,
                    'action': 'backtrack'
                })
        
        return False
    
    def _select_cell_mrv(self, grid):
        """Select cell with minimum remaining values."""
        min_remaining = self.grid_size + 1
        best_cell = None
        
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if grid[row][col] == 0:
                    possible = self._get_possible_values(grid, row, col)
                    if len(possible) < min_remaining:
                        min_remaining = len(possible)
                        best_cell = (row, col)
                        
                        if min_remaining == 1:
                            return best_cell
        
        return best_cell
    
    def _get_values_lcv(self, grid, row, col):
        """Order values by least constraining value."""
        possible_values = self._get_possible_values(grid, row, col)
        
        value_constraints = []
        for value in possible_values:
            eliminated = self._count_eliminations(grid, row, col, value)
            value_constraints.append((eliminated, value))
        
        value_constraints.sort()
        return [value for _, value in value_constraints]
    
    def _count_eliminations(self, grid, row, col, value):
        """Count how many options this value eliminates."""
        eliminated = 0
        
        # Check row impact
        for c in range(self.grid_size):
            if c != col and grid[row][c] == 0:
                if value in self._get_possible_values(grid, row, c):
                    eliminated += 1
        
        # Check column impact
        for r in range(self.grid_size):
            if r != row and grid[r][col] == 0:
                if value in self._get_possible_values(grid, r, col):
                    eliminated += 1
        
        # Check box impact
        box_row = (row // self.box_size) * self.box_size
        box_col = (col // self.box_size) * self.box_size
        
        for r in range(box_row, box_row + self.box_size):
            for c in range(box_col, box_col + self.box_size):
                if (r != row or c != col) and grid[r][c] == 0:
                    if value in self._get_possible_values(grid, r, c):
                        eliminated += 1
        
        return eliminated
    
    def _get_possible_values(self, grid, row, col):
        """Get all possible values for a cell."""
        if grid[row][col] != 0:
            return []
        
        possible = []
        for value in range(1, self.grid_size + 1):
            if self._is_valid_move(grid, row, col, value):
                possible.append(value)
        
        return possible
    
    def _is_valid_move(self, grid, row, col, value):
        """Check if move is valid."""
        # Check row
        for c in range(self.grid_size):
            if grid[row][c] == value:
                return False
        
        # Check column
        for r in range(self.grid_size):
            if grid[r][col] == value:
                return False
        
        # Check box
        box_row = (row // self.box_size) * self.box_size
        box_col = (col // self.box_size) * self.box_size
        
        for r in range(box_row, box_row + self.box_size):
            for c in range(box_col, box_col + self.box_size):
                if grid[r][c] == value:
                    return False
        
        return True

def create_variable_puzzle(grid_type, difficulty='medium'):
    """
    Create a variable-size Sudoku puzzle.
    grid_type: '2x2', '3x3', or '4x4'
    """
    grid_sizes = {
        '2x2': 4,
        '3x3': 9,
        '4x4': 16
    }
    
    if grid_type not in grid_sizes:
        raise ValueError(f"Unsupported grid type: {grid_type}")
    
    grid_size = grid_sizes[grid_type]
    generator = VariableSudokuGenerator(grid_size)
    
    return generator.generate_puzzle(difficulty)