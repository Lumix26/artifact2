from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException




class Crawler:
    """
    La classe Crawler rappresenta l'implementazione della funzionalità di ricerca ed estrazione del contenuto
    di interesse, su cui poi effettuare lo scraping, avanzando fra le varie risorse web.
    In questa specifica implementazione, per questione di immediatezza e velocità, mi sono legato molto allo 
    specifico contesto, non applicando il principio di Astrazione, di conseguenza questo Crawler è pensato per
    lavorare sulla specifica istanza che sto affrontando.
    """

    driver = webdriver.Firefox()
    
    avaible_models_links = []
    """
    Contiene tutti i link, come stringa, che riportano alla pagina del modello i-esimo
    """



    def __init__(self, url):
        self.url = url
        self.driver.get(url=url)


    def crawl(self):
        """
        Naviga fra le risorse disponibili ed estrae il contenuto di interesse.
        N.b il Driver ad esecuzione conclusa viene chiuso.
        """
        

        while True:

            #Devo estrarre tutti i link relativi ai modelli, contenuti nella i-esima pagina
            self._excract_links()
        
            try:
                #la find mi restituisce una lista contentente [Previous,Next]
                next_button = self.driver.find_elements(By.CSS_SELECTOR,"a.flex.items-center.rounded-lg")[1]
                next_button.click()
            except Exception as e:
                #Non mi interessa gestire l'eccezzione ma voglio solo bloccare il ciclo
                break
        
        self.driver.quit()

    def crawl_limited(self,n):

        wait = WebDriverWait(self.driver, 5)

        for _ in range(n):
            
            wait.until(self._excract_links)

            next_button = self.driver.find_elements(By.CSS_SELECTOR,"a.flex.items-center.rounded-lg")[1]
            next_button.click()

        self.driver.quit()

    
    def _excract_links(self,driver):
        """
        Estrazione degli URL relativi ai modelli
        """

        try:
            links = self.driver.find_elements(By.CSS_SELECTOR,"a.block.p-2")

            for link in links:
                self.avaible_models_links.append(link.get_attribute("href"))
        
            return True
        except Exception as e:
            print(e)
            return False


    def get_links(self):
        return self.avaible_models_links
    
    def save_on_file(self):

        with open("crawler_output3.txt","w") as file:
            for link in self.avaible_models_links:
                file.write(f"{link} \n")


def main():

    crawler = Crawler("https://huggingface.co/models?pipeline_tag=question-answering&sort=trending")

    crawler.crawl_limited(10)

    crawler.save_on_file()


if __name__ == "__main__":
    main()