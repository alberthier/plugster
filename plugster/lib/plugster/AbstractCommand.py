class AbstractCommand:

    def __init__(self, pipeline):
        self.pipeline = pipeline


    def do(self):
        pass


    def undo(self):
        pass
