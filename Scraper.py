import time
#from selenium import webdriver
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


    validated = {}

    def __init__(self, url_model:str) -> None:
        self.url = url_model
        #self.driver = webdriver.Firefox()
        #self.driver.get(self.url)
        #RICORDA SEMPRE DI PULIRE GLI URL DA SPAZI BIANCHI
        try:
            response = requests.get(self.url.strip())
            if response.status_code == 200:
                self.soup = BeautifulSoup(response.text,"html.parser")
        except Exception as e:
            #TO DO impostare una flag che blocca lo scrape
            pass
        #self.soup = BeautifulSoup(self.driver.page_source,"html.parser")
        self.dizionario = {}




    def _extract_info_tags(self):
        """
        Funziona
        """
        
        regex = re.compile("relative group flex items-center")

        try:
            info_tags = self.soup.find_all(class_=regex)

            stripped = [tag.get_text(strip=True) for tag in info_tags]

            result = self._lowerize_strings(stripped)

            return result
        
        except Exception as e:
            print(e)


    def _populate_dict(self):
        """
        Funziona
        """

        tags:list[str] = self._extract_info_tags()

        for phrase in tags:
            words = re.split(r',|\s',phrase)
            for word in words:
                tmp = word.strip()
                if tmp != '':
                    if tmp not in self.dizionario:
                        self.dizionario[tmp] = 1
                    else:
                        self.dizionario[tmp] = self.dizionario[tmp]+1


    def _lowerize_strings(self, tokens:list[str]):
        """
        Funziona
        """

        result:list[str] = []

        for token in tokens:
            result.append(token.lower())
        
        return result
    


    def scrape(self, keywords:list[str]):
        """
        Funziona
        """

        count = 0

        not_found:list[str] = []

        self._populate_dict()

        lower_kws = self._lowerize_strings(keywords)

        for kw in lower_kws:
            try:
                if self.dizionario[kw] >= 1:
                    count = count+1
            except KeyError as e:
                #TO-DO salvare quale tag non è presente per l'i-esimo modello.
                not_found.append(kw)
        
        if count >= len(keywords)/ 3:
            
            self.validated[self.url] = [
                #Molto costosa, sto creando una lista con i tag trovati
                [x for x in lower_kws if x not in not_found],
                not_found
            ]
        #self.driver.quit()


    def get_scraped(self):
        return self.validated 





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