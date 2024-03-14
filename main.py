import time
from Scraper import Scraper
import threading
import os
from multiprocessing import Process
import re
import requests
from bs4 import BeautifulSoup
from multiprocessing import Lock, Manager
import multiprocessing


manager = Manager()

output = manager.dict()

check = manager.list()

lock = Lock()


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

lower_bound = 10


def split_into_chunks(urls, n_thread):
    avg_chunk_size = len(urls) // n_thread
    remainder = len(urls) % n_thread

    chunks = []
    index = 0

    for i in range(n_thread):
        chunk_size = avg_chunk_size + (1 if i < remainder else 0)
        chunk = urls[index : index + chunk_size]
        chunks.append(chunk)

        index += chunk_size
    
    return chunks

def esecuzione_parallela(urls, n_thread):
    chunks = split_into_chunks(urls, n_thread)
    threads:list[Process] = []

    for chunk in chunks:
        thread = Process(target=scrape, args=(chunk,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


def scrape(urls:list[str]):

    count_elem = 0

    pesi = {
        regexs[0] : [False, 4],
        regexs[1] : [False,3],
        regexs[2] : [False,3],
        regexs[3] : [False,2],
        regexs[4] : [False,2],
        regexs[5] : [False,3],
        regexs[6] : [False,3],
        regexs[7] : [False,3]
    }

    for url in urls:
        count_elem = count_elem+1
        print(f"Il processo {multiprocessing.current_process().ident} sta lavorando {url}", end='\r')
        sum = 0
        try:
            response = requests.get(url.strip())
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                for regex in regexs:
                    if soup.find(string=regex):
                        pesi[regex][0] = True
                #Calcolo fun_obiettivo
                for key in pesi:
                    if pesi[key][0]:
                        sum = sum + pesi[key][1]

                if sum >= lower_bound:
                    with lock:
                        output[url.strip()] = [key for key in pesi if pesi[key][0] == False]

                #azzera pesi
                for key in pesi:
                    pesi[key][0] = False

            else:
                #TO-DO definire eccezzione in caso di url corrotto
                pass
        except Exception as e:
            #TO-DO definire eccezzione in caso di url corrotto
            pass
    
    with lock:
        check.append(count_elem)



def main():


    urls = []

    try:
        with open("crawler_output4.txt","r") as file:
            for riga in file:
                urls.append(riga)
    except FileNotFoundError as e:
        print("File non trovato")


    start = time.time()

    esecuzione_parallela(urls, os.cpu_count())


    end = time.time()

    print(f"Tempo impiegato: {end - start} s")

    print(output)
    print(check)

    with open("scraper_output15.txt","w") as file:
        for key in output:
            file.write(f"Modello ottenuto: {str(key)} \nParametri non trovati: {', '.join(map(str,output[key]))} \n")
            file.write("\n")

if __name__ == "__main__":
    main()