"""
Visualization module for Sudoku solver backtracking algorithm.
This generates step data for visualizing the backtracking process.
"""
import copy
import random
import time

class BacktrackingVisualizer:
    def __init__(self, n=3):
        self.n = n  # Size of each box
        self.size = n * n  # Total grid size
        self.steps = []
        self.decision_nodes = []
        self.current_step = 0
    
    def reset(self):
        """Reset the visualization data."""
        self.steps = []
        self.decision_nodes = []
        self.current_step = 0
    
    def visualize_backtracking(self, grid):
        """Generate visualization data for the backtracking algorithm."""
        # Make a deep copy to avoid modifying the original grid
        self.grid = copy.deepcopy(grid)
        self.reset()
        
        # Add the initial state
        self.steps.append({
            "grid": copy.deepcopy(self.grid),
            "message": "Starting the backtracking algorithm",
            "row": -1, 
            "col": -1,
            "value": -1,
            "is_decision": False,
            "is_backtrack": False
        })
        
        # Start the backtracking process
        self._solve_with_visualization(0, 0)
        
        # Return the steps and decision tree data
        return self.steps, self.decision_nodes
    
    def _solve_with_visualization(self, row, col):
        """Recursive function to solve the Sudoku puzzle with visualization."""
        # If we've reached the end of the grid, we're done
        if row == self.size:
            return True
        
        # If this cell is already filled, move to the next cell
        if self.grid[row][col] != 0:
            # Calculate next position
            next_row, next_col = (row, col + 1) if col < self.size - 1 else (row + 1, 0)
            return self._solve_with_visualization(next_row, next_col)
        
        # Try numbers 1 to size for this cell
        nums = list(range(1, self.size + 1))
        random.shuffle(nums)  # Try numbers in random order for more interesting visualization
        
        parent_node_id = len(self.steps) - 1
        
        for num in nums:
            # Check if this number is valid in this position
            if self._is_valid(row, col, num):
                # Place the number
                self.grid[row][col] = num
                
                # Add this decision point to our steps
                self.steps.append({
                    "grid": copy.deepcopy(self.grid),
                    "message": f"Trying {num} at position ({row+1}, {col+1})",
                    "row": row,
                    "col": col,
                    "value": num,
                    "is_decision": True,
                    "is_backtrack": False
                })
                
                current_node_id = len(self.steps) - 1
                
                # Record decision tree node
                self.decision_nodes.append({
                    "id": current_node_id,
                    "parent": parent_node_id,
                    "row": row,
                    "col": col,
                    "value": num,
                    "success": None  # We don't know yet
                })
                
                # Calculate next position
                next_row, next_col = (row, col + 1) if col < self.size - 1 else (row + 1, 0)
                
                # Recursive call
                if self._solve_with_visualization(next_row, next_col):
                    # Update decision node as successful
                    self._update_decision_node_status(current_node_id, True)
                    return True
                
                # If we get here, this number didn't work
                self.grid[row][col] = 0
                
                # Add backtracking step
                self.steps.append({
                    "grid": copy.deepcopy(self.grid),
                    "message": f"Backtracking: {num} at position ({row+1}, {col+1}) didn't work",
                    "row": row,
                    "col": col,
                    "value": 0,
                    "is_decision": False,
                    "is_backtrack": True
                })
                
                # Update decision node as failed
                self._update_decision_node_status(current_node_id, False)
                
                # Add a small delay for visualization purposes
                time.sleep(0.001)
        
        # If no number worked, return False (we'll need to backtrack)
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
    
    def _update_decision_node_status(self, node_id, success):
        """Update the success status of a decision node."""
        for i, node in enumerate(self.decision_nodes):
            if node["id"] == node_id:
                self.decision_nodes[i]["success"] = success
                break

def get_visualization_data(puzzle, n=3):
    """
    Generate visualization data for the given puzzle.
    Returns the steps and decision tree data.
    """
    visualizer = BacktrackingVisualizer(n)
    return visualizer.visualize_backtracking(puzzle)