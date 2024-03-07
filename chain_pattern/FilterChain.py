from ConcreteF1 import ConcreteF1
from ConcreteF2 import ConcreteF2
from ConcreteF3 import ConcreteF3


class FilterChain:



    filter1 = ConcreteF1()
    filter2 = ConcreteF2(filter1)
    filter3 = ConcreteF3(filter2)

    def __init__(self, kws1:list, kws2:list, kws3:list) -> None:
        """
        Args:
            kws1 rappresenta una lista di possibili filtri da applicare al primo filtro
        Args:
            kws2 rappresenta una lista di possibili filtri da applicare al secondo filtro
        Args:
            kws3 rappresenta una lista di possibili filtri da applicare al terzo filtro"""
        self.filter1.set_pattern(kws1)
        self.filter2.set_pattern(kws2)
        self.filter3.set_pattern(kws3)
    

    def filter(self,request):
        self.filter3.handle(request)

    def get_filtered(self):
        return self.filter3.filtered
    
    def clean(self):
        self.filter3.filtered.clear()