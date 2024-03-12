import time
from Scraper import Scraper
import threading
import os


# def task(urls):
#     i = 1

#     for url in urls:
#         print(f"Il thread {threading.current_thread.__name__} sta elaborando il modello {i}", end='\r')
#         i += 1

#         scraper = Scraper(url)
        
#         scraper.scrape()


# def split_into_chunks(urls, n_thread):
#     avg_chunk_size = len(urls) // n_thread
#     remainder = len(urls) % n_thread

#     chunks = []
#     index = 0

#     for i in range(n_thread):
#         chunk_size = avg_chunk_size + (1 if i < remainder else 0)
#         chunk = urls[index : index + chunk_size]
#         chunks.append(chunk)

#         index += chunk_size
    
#     return chunks

# def esecuzione_parallela(urls, n_thread):
#     chunks = split_into_chunks(urls, n_thread)
#     threads:list[threading.Thread] = []

#     for chunk in chunks:
#         thread = threading.Thread(target=task, args=(chunk,))
#         thread.start()
#         threads.append(thread)

#     for thread in threads:
#         thread.join()


def main():


    urls = []


    with open("crawler_output4.txt","r") as file:
        for riga in file:
            urls.append(riga)



    i = 1
    start = time.time()

    #esecuzione_parallela(urls, os.cpu_count())

    for url in urls:
        print(f"Elaborando modello {i}", end ='\r')
        i = i+1

        scraper = Scraper(url)
        
        scraper.scrape()


    #scraper = Scraper("")
    result = scraper.get_scraped()
        
    end = time.time()

    print(f"Tempo impiegato: {end - start} s")

    with open("scraper_output10.txt","w") as file:
        for key in result:
            file.write(f"Modello ottenuto: {str(key)} \nParametri non trovati: {', '.join(map(str,result[key]))} \n")
            file.write("\n")

if __name__ == "__main__":
    main()