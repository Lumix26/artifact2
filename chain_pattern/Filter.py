class Filter:
    """
    Interfaccia che definisce il pattern Chain of responsability."""

    def __init__(self, successor=None) -> None:
        self.successor = successor
        self.filtered = []
    

    def handle(self, request):
        #Se esiste il successore, quindi not None
        if self.successor:
            self.successor.handle(request)