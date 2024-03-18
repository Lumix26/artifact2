from multiprocessing import Manager, Process, Lock
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import multiprocessing
from selenium.common.exceptions import NoSuchElementException, TimeoutException

class Validator:



    

    context = "Revelis è una startup innovativa che realizza soluzioni di Intelligenza Artificiale grazie al Big Data management. La combinazione di Machine Learning e Deep Learning ed il ragionamento automatico, consente l’analisi dei Big Data e la correlazione di informazioni, per la previsione dei fenomeni e l’ottimizzazione dei processi aziendali. Inoltre, l’uso di tecniche di explanation consente ai decisori di comprendere le cause e le caratteristiche dei modelli decisionali."

    manager = Manager()
    question_answer = manager.dict()
    result = manager.dict()

    lock = Lock()

    questions = [
        "Chi è revelis?",
        "Cosa comporta l'uso di tecniche di explanation?",
        "Cosa realizza Revelis?",
        "Revelis fa uso Machine Learning?",
        "Revelis ottimizza i processi aziendali?",
        "Revelis è una panetteria?"
    ]

    answers = [
        "una startup innovativa",
        "comprendere le cause e le caratteristiche dei modelli decisionali",
        "soluzioni di Intelligenza Artificiale",
        "si",
        "si",
        "no"
    ]

    for i,question in enumerate(questions):
        
        question_answer[questions[i]] = [
                answers[i],
                1 if i < 3 else 2
            ]




    def __init__(self, urls:list[str]) -> None:
        self.urls = urls

    

    def _validate(self,chunk:list[str]):

        print(f"Processo {multiprocessing.current_process().ident}")

        for url in chunk:

            flag = True

            driver = webdriver.Firefox()

            #creazione del dizionario che terrà traccia delle risposte corrette date
            local_weigth = {}

            
            for question in self.question_answer.keys():
                local_weigth[question] = False

            #stripped = url.strip()

            #carichiamo l'url del modello
            driver.get(url)

            try:

                #localizzare il campo context
                context_field = WebDriverWait(driver,10).until(
                    EC.presence_of_element_located(
                        (By.XPATH,"/html/body/div/main/div[2]/section[2]/div[5]/div/form/div[3]/label/span[2]")
                    )
                )

                try:
                    
                    #localizzare bottone compute
                    compute = WebDriverWait(driver,10).until(
                        EC.presence_of_element_located(
                            (By.XPATH,"/html/body/div/main/div[2]/section[2]/div[5]/div/form/div[3]/div/button")
                        )
                    )
                    
                    #localizzare question field
                    try:

                        question_field = WebDriverWait(driver,10).until(
                            EC.presence_of_element_located(
                                (By.XPATH,"/html/body/div/main/div[2]/section[2]/div[5]/div/form/div[3]/div/input")
                            )
                        )


                        #Carico il context
                        context_field.clear()
                        driver.implicitly_wait(1)
                        context_field.send_keys(self.context)

                        for key_qstn in self.question_answer.keys():

                            #Scrittura domanda
                            question_field.click()
                            driver.implicitly_wait(1)
                            question_field.clear()
                            driver.implicitly_wait(1)
                            question_field.send_keys(key_qstn)

                            #Clicco compute
                            driver.implicitly_wait(1)
                            compute.click()

                            #cerco la risposta ottenuta
                            try:

                                output = WebDriverWait(driver,30).until(
                                    EC.presence_of_element_located(
                                        (By.XPATH,"/html/body/div/main/div[2]/section[2]/div[5]/div/form/div[5]/span[1]")
                                    )
                                )


                                #TO-DO verifica risposta
                                if output.text == self.question_answer[key_qstn][0]:
                                    local_weigth[key_qstn] = True

                            except TimeoutException as to:
                                print(f"Il modello {url} ha generato un Timeout")
                            except NoSuchElementException as ne:
                                print(f"Il modello {url} non ha trovato il campo -Risposta-")


                    except TimeoutException as to:
                        flag = False
                        driver.quit()
                        print(f"Il modello {url} ha generato un Timeout")
                    except NoSuchElementException as ne:
                        flag = False
                        driver.quit()
                        print(f"Il modello {url} non ha trovato il campo -question-")
                    #fine try question field
                        
                except TimeoutException as to:
                    flag = False
                    driver.quit()
                    print(f"Il modello {url} ha generato un Timeout")
                except NoSuchElementException as ne:
                    flag = False
                    driver.quit()
                    print(f"Il modello {url} non ha trovato il campo -compute-")
                #fine try compute

            except TimeoutException as to:
                flag = False
                driver.quit()
                print(f"Il modello {url} ha generato un Timeout")
            except NoSuchElementException as ne:
                flag = False
                driver.quit()
                print(f"Il modello {url} non ha trovato il campo -context-")
            #fine try context
                 

            #valutazione risposte modello
            if self._fun_obiettivo(local_weigth) >= 3:
                #TO-DO aggiungere il modello alla struttura che conterrà i modelli positivi
                self.result[url] = [ key for key in local_weigth if not local_weigth[key]]
        
            driver.quit()



    def _fun_obiettivo(self,diz:dict):
        sum = 0

        for key in diz:
            if diz[key]:
                sum = sum + self.question_answer[key][1]
        
        return sum


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
            thread = Process(target=self._validate, args=(chunk,))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()

    def get_result(self):
        return self.result