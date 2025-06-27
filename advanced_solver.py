"""
Advanced Sudoku solver using MRV and LCV heuristics.
This demonstrates enhanced backtracking algorithms for comparison.
"""
import time
import copy

class AdvancedSudokuSolver:
    def __init__(self):
        self.backtrack_count = 0
        self.constraint_checks = 0
        self.start_time = 0
        self.solving_steps = []
        
    def solve_with_heuristics(self, grid):
        """
        Solve Sudoku using MRV (Minimum Remaining Values) and 
        LCV (Least Constraining Value) heuristics
        """
        self.backtrack_count = 0
        self.constraint_checks = 0
        self.solving_steps = []
        self.start_time = time.time()
        
        # Create a working copy
        working_grid = [row[:] for row in grid]
        
        # Solve using enhanced backtracking
        success = self._solve_with_mrv_lcv(working_grid)
        
        solving_time = time.time() - self.start_time
        
        return {
            'solved': success,
            'grid': working_grid if success else grid,
            'stats': {
                'backtrack_count': self.backtrack_count,
                'constraint_checks': self.constraint_checks,
                'solving_time': solving_time,
                'steps': len(self.solving_steps)
            },
            'steps': self.solving_steps
        }
    
    def _solve_with_mrv_lcv(self, grid):
        """
        Recursive solver using MRV and LCV heuristics
        """
        # Find the best cell using MRV heuristic
        cell = self._select_cell_mrv(grid)
        
        if cell is None:
            return True  # All cells filled, puzzle solved
        
        row, col = cell
        
        # Get possible values ordered by LCV heuristic
        possible_values = self._get_values_lcv(grid, row, col)
        
        for value in possible_values:
            self.constraint_checks += 1
            
            if self._is_valid_move(grid, row, col, value):
                # Make the move
                grid[row][col] = value
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'value': value,
                    'action': 'place',
                    'heuristic': 'MRV+LCV'
                })
                
                # Recursively solve
                if self._solve_with_mrv_lcv(grid):
                    return True
                
                # Backtrack
                grid[row][col] = 0
                self.backtrack_count += 1
                self.solving_steps.append({
                    'row': row,
                    'col': col,
                    'value': value,
                    'action': 'backtrack',
                    'heuristic': 'MRV+LCV'
                })
        
        return False
    
    def _select_cell_mrv(self, grid):
        """
        MRV Heuristic: Select the empty cell with the fewest possible values
        """
        min_remaining_values = 10
        best_cell = None
        
        for row in range(9):
            for col in range(9):
                if grid[row][col] == 0:
                    possible_values = self._get_possible_values(grid, row, col)
                    remaining_count = len(possible_values)
                    
                    if remaining_count < min_remaining_values:
                        min_remaining_values = remaining_count
                        best_cell = (row, col)
                        
                        # If we find a cell with only one possibility, use it immediately
                        if remaining_count == 1:
                            return best_cell
        
        return best_cell
    
    def _get_values_lcv(self, grid, row, col):
        """
        LCV Heuristic: Order values by least constraining (affects fewest other cells)
        """
        possible_values = self._get_possible_values(grid, row, col)
        
        # Calculate how many options each value eliminates for other cells
        value_constraints = []
        
        for value in possible_values:
            eliminated_options = self._count_eliminated_options(grid, row, col, value)
            value_constraints.append((eliminated_options, value))
        
        # Sort by fewest eliminations (least constraining first)
        value_constraints.sort()
        
        return [value for _, value in value_constraints]
    
    def _count_eliminated_options(self, grid, row, col, value):
        """
        Count how many options this value would eliminate for other empty cells
        """
        eliminated = 0
        
        # Check impact on row
        for c in range(9):
            if c != col and grid[row][c] == 0:
                if value in self._get_possible_values(grid, row, c):
                    eliminated += 1
        
        # Check impact on column
        for r in range(9):
            if r != row and grid[r][col] == 0:
                if value in self._get_possible_values(grid, r, col):
                    eliminated += 1
        
        # Check impact on 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if (r != row or c != col) and grid[r][c] == 0:
                    if value in self._get_possible_values(grid, r, c):
                        eliminated += 1
        
        return eliminated
    
    def _get_possible_values(self, grid, row, col):
        """
        Get all possible values for a cell
        """
        if grid[row][col] != 0:
            return []
        
        possible = []
        for value in range(1, 10):
            if self._is_valid_move(grid, row, col, value):
                possible.append(value)
        
        return possible
    
    def _is_valid_move(self, grid, row, col, value):
        """
        Check if placing a value at (row, col) is valid
        """
        # Check row
        for c in range(9):
            if grid[row][c] == value:
                return False
        
        # Check column
        for r in range(9):
            if grid[r][col] == value:
                return False
        
        # Check 3x3 box
        box_row, box_col = 3 * (row // 3), 3 * (col // 3)
        for r in range(box_row, box_row + 3):
            for c in range(box_col, box_col + 3):
                if grid[r][c] == value:
                    return False
        
        return True

def compare_algorithms(puzzle):
    """
    Compare basic backtracking vs MRV+LCV heuristics
    """
    try:
        from visualization import BacktrackingVisualizer
        
        # Test basic backtracking
        basic_visualizer = BacktrackingVisualizer()
        basic_data = basic_visualizer.visualize_backtracking([row[:] for row in puzzle])
        
        # Test advanced heuristics
        advanced_solver = AdvancedSudokuSolver()
        advanced_result = advanced_solver.solve_with_heuristics([row[:] for row in puzzle])
        
        # Handle the tuple return from basic visualizer
        if isinstance(basic_data, tuple) and len(basic_data) >= 2:
            basic_steps = basic_data[0] if basic_data[0] else []
        else:
            basic_steps = []
        
        advanced_steps = advanced_result.get('steps', [])
        
        basic_backtrack_count = 0
        if basic_steps:
            basic_backtrack_count = sum(1 for s in basic_steps if isinstance(s, dict) and s.get('action') == 'backtrack')
        
        return {
            'basic': {
                'steps': len(basic_steps),
                'backtrack_count': basic_backtrack_count,
                'solving_time': 0
            },
            'advanced': advanced_result.get('stats', {}),
            'improvement_factor': len(basic_steps) / len(advanced_steps) if advanced_steps and len(advanced_steps) > 0 else 1
        }
    except Exception as e:
        return {
            'basic': {'steps': 0, 'backtrack_count': 0, 'solving_time': 0},
            'advanced': {'steps': 0, 'backtrack_count': 0, 'solving_time': 0},
            'improvement_factor': 1,
            'error': str(e)
        }