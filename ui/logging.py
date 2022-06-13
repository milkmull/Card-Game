
class Logging:
    def __init__(self):
        self.logs = []
        
    def get_logs(self):
        logs = self.logs.copy()
        self.logs.clear()
        return logs
        
    def clear_logs(self):
        self.logs.clear()
        
    def add_log(self, log):
        self.logs.append(log)
        
    def pop_log(self):
        if self.logs:
            return self.logs.pop(-1)
            
    def undo_log(self):
        pass
        
    def redo_log(self):
        pass
    