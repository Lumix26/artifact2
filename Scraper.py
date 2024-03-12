import time
from bs4 import BeautifulSoup
import re
import requests


class Scraper:
    """
    v1. La seguente versione prevede l'uso anche nello scraper del driver di selenium, ciò comporta
    un grosso incremento in termini di complessità temporale, per analizzare 1880 modelli sono state
    necessarie 4h, a fronte di ciò è necessaria eseguire un'analisi approfondita del corpus medio delle 
    pagine contenenti i modelli per verificare se è necessario interagire ulteriormente con gli elementi mediante
    driver.
    Author: Marco"""

    #Analizzare questo snippet
    #target.find_all(lambda tag:tag.name=="li" and re.search(regex,tag.text))

    lower_bound = 13


    regexs = [
        re.compile(r'[F|f]ine-tune[d]*'),
        re.compile(r'[I|i]talian'),
        re.compile(r'[E|e]nglish'),
        re.compile(r'[C|c](PU|pu)'),
        re.compile(r'[G|g](PU|pu)'),
        re.compile(r'[G|g](pt|PT)'),
        re.compile(r'(\d)*[BERT](\d)*'),
        re.compile(r'T5')
    ]

    #rappresentazione Sum(CiXi)
    #costo modello ideale z*
    

    to_validate = {}

    def __init__(self, url_model:str) -> None:
            self.url = url_model
            self.flag = True
            self.kws_wg = {
                self.regexs[0] : [False, 4],
                self.regexs[1] : [False,3],
                self.regexs[2] : [False,3],
                self.regexs[3] : [False,2],
                self.regexs[4] : [False,2],
                self.regexs[5] : [False,3],
                self.regexs[6] : [False,3],
                self.regexs[7] : [False,3]
            }

            #RICORDA SEMPRE DI PULIRE GLI URL DA SPAZI BIANCHI
            try:
                response = requests.get(self.url.strip())
                if response.status_code == 200:
                    self.soup = BeautifulSoup(response.text,"html.parser")
                else:
                    self.flag = False
            except Exception as e:
                #TO DO impostare una flag che blocca lo scrape
                self.flag = False
        




    def scrape(self):
        if(self.flag):
            # result = [ {regex : self.soup.find_all(string=regex)} for regex in self.regexs ]
            # for diz in result:
            #     for key in diz:
            #         if len(diz[key]) > 0:
            #             self.kws_wg[key][0] = True
            for regex in self.regexs:
                if self.soup.find(string=regex):
                    self.kws_wg[regex][0] = True
            
            if self._fun_obiettivo() >= self.lower_bound:
                self.to_validate[self.url] = [key for key in self.kws_wg if self.kws_wg[key][0] == False]

    def _fun_obiettivo(self):
        sum = 0

        for key in self.kws_wg:
            if self.kws_wg[key][0] == True:
                sum = sum + self.kws_wg[key][1]
        
        return sum

    def get_scraped(self):
        return self.to_validate

    




def main():
    
    scraper = Scraper("https://huggingface.co/CohereForAI/aya-101")

    KEYWORDS_DESIRED = [
        "Use",
        "USAGE",
        "CPU",
        "training",
        "languages",
        "finetuning",
        "bias",
        "evaluation"
    ]


    
    start = time.time()
    scraper.scrape(KEYWORDS_DESIRED)
    end = time.time()

    result = scraper.get_scraped()

    for key in result:
        print(f"Modello ottenuto: {key} \n Parametri trovati: {', '.join(result[key][0])} \n Parametri non trovati: {', '.join(result[key][1])}")
    
    print(f"Tempo di esecuzione: {end-start} s")



if __name__ == "__main__":
    main()