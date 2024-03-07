from Filter import Filter
import re

class ConcreteF3(Filter):
    regex = []
    
    def set_pattern(self, patterns:list):
        
        for pattern in patterns:
            self.regex.append(re.compile(pattern,re.IGNORECASE))
    

    def handle(self, request):
        count = 0

        for r in self.regex:
            if re.search(r,request):
                count = count+1
                self.filtered.append(request)
        
        if count == 0:
            super().handle(request)
            #TO-DO aggiungere logger nel branch else