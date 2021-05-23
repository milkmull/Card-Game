import copy

class Yo:
    def __init__(self):
        return
    
    def __deepcopy__(self, memo):
        print(memo)
        print(id(self))

class Card:
    def __init__(self, name, cid, type):

        self.name = name
        self.cid = cid
        self.type = type
        
        self.mode = 0
        self.counter = 0
        
        self.owner = None
        
        self.tag = None
        self.wait = None
        
        self.mult = True
        
        self.ref = None
        
        self.yo = Yo()
        
test = Card('yo', 1, 'yeet')

copy.deepcopy(test)