from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException

from bs4 import BeautifulSoup

import re

def main():

    current_url = "https://huggingface.co/models?pipeline_tag=text-generation&sort=trending"
    
    driver = webdriver.Firefox()
    driver.get(current_url)

    pages = []

    wait = WebDriverWait(driver, 10)

    #while True:
            
            # driver.get(current_url)
            # #Inserisco nella lista l'i-esima pagina html
            # pages.append(driver.page_source)

            # try:
            #     e = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR,"a.flex.items-center.rounded-lg")))
            #     next = driver.find_elements(By.CSS_SELECTOR,"a.flex.items-center.rounded-lg")[1]
            #     print(next.tag_name)
            #     next.click()
            #     current_url = driver.current_url
            # except NoSuchElementException as e:
            #     break
            # finally:
            #     driver.quit()
    # with open("pages.txt","w") as file:

    #     while True:
    #         try:
    #             next = driver.find_elements(By.CSS_SELECTOR,"a.flex.items-center.rounded-lg")[1]
    #             next.click()
    #             file.write(driver.page_source)
    #             file.write("\n")
    #         except Exception as e:
    #             break
    
    # driver.quit()



    page_source = driver.page_source

    soup = BeautifulSoup(page_source,"html.parser")

    stripped = []
    result = []

    #creo il patter regex
    regex = re.compile("relative group flex items-center")
    try:
        key_words = soup.find_all(class_=regex)

        for info in key_words:
           stripped.append(info.get_text(strip=True))
        
        print(regex)
        for s in stripped:
            print(s)

        regex = desidered_requirements()

        for r in regex:
            for s in stripped:
                if r.search(s, re.IGNORECASE):
                    result.append(s)
        

        for out in result:
            print(out)

    except Exception as e:
        print(f"Errore nella find -->{e}")
    finally:
        driver.quit()





    """
    Questa parte funziona
    """
    # try:
    #     e = driver.find_element(By.CSS_SELECTOR, "h4.relative.group.flex.items-center")

    #     print(e.text)
    # except NoSuchElementException as e:
    #     print(f"La find ha fallito! --->{e}")
    # finally:
    #     driver.quit()


def desidered_requirements():
    desidered = [
        "CPU",
        "TEXT STRING",
        "QUESTION"
    ]

    res = [ re.compile(regex) for regex in desidered]

    return res


def save_on_file(pages):
        with open("pages_source.txt", "w") as file:
            for page in pages:
                file.write(page)
                file.write("\n")



if __name__ == "__main__":
    main()