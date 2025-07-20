import copy
import random
import time

class BacktrackingVisualizer:
    def __init__(self):
        self.steps = []
        self.decision_nodes = []
        self.current_step = 0
    
    def reset(self):
        
        self.steps = []
        self.decision_nodes = []
        self.current_step = 0
    
    def visualize_backtracking(self, grid):
        
        
        self.grid = copy.deepcopy(grid)
        self.reset()
        
        
        self.steps.append({
            "grid": copy.deepcopy(self.grid),
            "message": "Starting the backtracking algorithm",
            "row": -1, 
            "col": -1,
            "value": -1,
            "is_decision": False,
            "is_backtrack": False
        })
        
        
        self._solve_with_visualization(0, 0)
        
       
        return self.steps, self.decision_nodes
    
    def _solve_with_visualization(self, row, col):
        
        
        if row == 9:
            return True
        
        
        if self.grid[row][col] != 0:
            
            next_row, next_col = (row, col + 1) if col < 8 else (row + 1, 0)
            return self._solve_with_visualization(next_row, next_col)
        
        
        nums = list(range(1, 10))
        random.shuffle(nums)  
        parent_node_id = len(self.steps) - 1
        
        for num in nums:
            
            if self._is_valid(row, col, num):
                
                self.grid[row][col] = num
                
                
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
                
                
                self.decision_nodes.append({
                    "id": current_node_id,
                    "parent": parent_node_id,
                    "row": row,
                    "col": col,
                    "value": num,
                    "success": None  
                })
                
                
                next_row, next_col = (row, col + 1) if col < 8 else (row + 1, 0)
                
                
                if self._solve_with_visualization(next_row, next_col):
                    
                    self._update_decision_node_status(current_node_id, True)
                    return True
                
                
                self.grid[row][col] = 0
                
                
                self.steps.append({
                    "grid": copy.deepcopy(self.grid),
                    "message": f"Backtracking: {num} at position ({row+1}, {col+1}) didn't work",
                    "row": row,
                    "col": col,
                    "value": 0,
                    "is_decision": False,
                    "is_backtrack": True
                })
                
                
                self._update_decision_node_status(current_node_id, False)
                
                
                time.sleep(0.001)
        
        
        return False
    
    def _is_valid(self, row, col, num):
        
        
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
    
    def _update_decision_node_status(self, node_id, success):
        
        for i, node in enumerate(self.decision_nodes):
            if node["id"] == node_id:
                self.decision_nodes[i]["success"] = success
                break

def get_visualization_data(puzzle):
    
    visualizer = BacktrackingVisualizer()
    return visualizer.visualize_backtracking(puzzle)