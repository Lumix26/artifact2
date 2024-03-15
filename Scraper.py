import time
from bs4 import BeautifulSoup
import re
import requests
import os
import multiprocessing
from multiprocessing import Lock, Manager, Process



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

    lock = Lock()

    manager = Manager()

    shared_dict = manager.dict()



    lower_bound = 10


    regexs = [
                re.compile(r'[F|f]ine-tune[d]*'),
                re.compile(r'[I|i]talian'),
                re.compile(r'[E|e]nglish'),
                re.compile(r'[C|c](PU|pu)'),
                re.compile(r'[G|g](PU|pu)'),
                re.compile(r'[G|g](pt|PT)'),
                re.compile(r'(\d)*[BERT](\d)*'),
                re.compile(r'T5'),
                re.compile(r'[L|l]lama'),
                re.compile(r'[M|m]istral'),
                re.compile(r'[G|g]emma')
            ]
    
    
    

    #rappresentazione Sum(CiXi)
    #costo modello ideale z*


    def __init__(self, urls:list[str]) -> None:
            self.urls = urls
        




    def _scrape(self,chunks:list[str]):

        pesi = {
            self.regexs[0] : [False, 4],
            self.regexs[1] : [False,3],
            self.regexs[2] : [False,3],
            self.regexs[3] : [False,2],
            self.regexs[4] : [False,2],
            self.regexs[5] : [False,3],
            self.regexs[6] : [False,3],
            self.regexs[7] : [False,3],
            self.regexs[8] : [False,3],
            self.regexs[9] : [False,3],
            self.regexs[10] :[False,3]
        }

        for url in chunks:

            #print(f"Processo {multiprocessing.current_process().ident} sta analizzando {url}", end='\r')
            stripped = url.strip()
            try:
                response = requests.get(stripped)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text,"html.parser")

                    for regex in self.regexs:
                        if soup.find(string=regex):
                            pesi[regex][0] = True
                    
                    if self._fun_obiettivo(pesi) >= self.lower_bound:
                        with self.lock:
                            self.shared_dict[stripped] = [key for key in pesi if pesi[key][0] == False]
                        
                        for key in pesi:
                            pesi[key][0] = False
                else:
                    #TO-DO handle corrupt urls
                    pass
            except Exception as e:
                #TO-DO handle connection error
                pass

    def _fun_obiettivo(self,pesi):
        sum = 0

        for key in pesi:
            if pesi[key][0] == True:
                sum = sum + pesi[key][1]
        
        return sum

    def get_result(self):
        return self.shared_dict
    
    def _split_into_chunks(self):
        n_process = os.cpu_count()

        avg_chunk_size = len(self.urls) // n_process
        remainder = len(self.urls) % n_process

        chunks = []
        index = 0

        for i in range(n_process):
            chunk_size = avg_chunk_size + (1 if i < remainder else 0)
            chunk = self.urls[index : index + chunk_size]
            chunks.append(chunk)

            index += chunk_size
        
        return chunks

    def run(self):

        chunks = self._split_into_chunks()
        threads:list[Process] = []

        for chunk in chunks:
            thread = Process(target=self._scrape, args=(chunk,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()



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