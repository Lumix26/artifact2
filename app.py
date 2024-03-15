import time
from Scraper import Scraper



def main():


    urls = []

    try:
        with open("crawler_output4.txt","r") as file:
            for riga in file:
                urls.append(riga)
    except FileNotFoundError as e:
        print("File non trovato")


    start = time.time()

    scraper = Scraper(urls)

    print(f"Elaborando..")

    scraper.run()

    end = time.time()

    output = scraper.get_result()

    print(scraper.get_llm_count())

    print(f"Esecuzione completata in {end-start} secondi")

    with open("scraper_output18.txt","w") as file:
        for key in output:
            file.write(f"Modello ottenuto: {str(key)} \nParametri non trovati: {', '.join(map(str,output[key]))} \n")
            file.write("\n")



if __name__ == "__main__":
    main()