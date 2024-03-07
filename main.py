import time
from Crawler import Crawler
from Scraper import Scraper


def main():

    # crawler = Crawler("https://huggingface.co/models?pipeline_tag=text2text-generation&sort=trending")

    # crawler.crawl()

    urls = []

    # DESIDERED_KEYWORDS = [
    #         "CPU",
    #         "USE",
    #         "USES",
    #         "LANGUAGES",
    #         "FINETUNING",
    #         "TUNING",
    #         "ITALIAN",
    #         "ITA",
    #         "IT",
    #         "USE",
    #         "TRAINING",
    #     ]

    with open("crawler_output3.txt","r") as file:
        for riga in file:
            urls.append(riga)


    start = time.time()

    for url in urls:
        scraper = Scraper(url)
        
        scraper.scrape()

    result = scraper.get_scraped()
        
    end = time.time()

    print(f"Tempo impiegato: {end - start} s")

    with open("scraper_output3.txt","w") as file:
        for key in result:
            file.write(f"Modello ottenuto: {key} \n Parametri non trovati: {', '.join(result[key])} \n")

if __name__ == "__main__":
    main()