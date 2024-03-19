import time
import requests
import json
from multiprocessing import Process, Manager, Lock
import multiprocessing
import os
import threading
import logging
from huggingface_hub import HfApi
from huggingface_hub import hf_api


class Validator:

    context = """
        Revelis è una startup innovativa che realizza soluzioni di Intelligenza Artificiale grazie al Big Data management. 
        La combinazione di Machine Learning e Deep Learning ed il ragionamento automatico, consente l'analisi dei Big Data e la correlazione di informazioni, per la previsione dei fenomeni e l'ottimizzazione dei processi aziendali. 
        Inoltre, l'uso di tecniche di explanation consente ai decisori di comprendere le cause e le caratteristiche dei modelli decisionali.
        Crediamo nelle idee, nella creatività e nell'entusiasmo dei nostri collaboratori e ci impegniamo per creare un ambiente di lavoro confortevole e stimolante.
        Promuoviamo costantemente la crescita professionale del nostro team di Big Data Analyst negli ambiti dell'Intelligenza Artificiale e dell'Advanced Analytics attraverso corsi di formazione e certificazioni professionali riconosciute internazionalmente.
    """

    manager = Manager()
    question_answer = manager.dict()
    result = manager.dict()


    lock = Lock()

    logger = logging.getLogger("__name__")
    

    #variabili d'uso dell'API

    API = HfApi()

    with open("secrets.json") as file:
        data = json.load(file)

    token = data["token"]

    headers = {
        "Authorization": f"Bearer {token}"
    }

    common_url = "https://api-inference.huggingface.co/models/"


    questions = [
        "Chi è revelis?",
        "Cosa comporta l'uso di tecniche di explanation?",
        "Cosa realizza Revelis?",
        "In cosa crediamo?",
        "Cosa promuoviamo?",
        "In cosa ci impegniamo?"
    ]

    answers = [
        "una startup innovativa",
        "comprendere le cause e le caratteristiche dei modelli decisionali",
        "soluzioni di Intelligenza Artificiale",
        "nelle idee, nella creatività e nell'entusiasmo",
        "la crescita professionale del nostro team di Big Data Analyst",
        "per creare un ambiente di lavoro confortevole e stimolante"
    ]

    for i,question in enumerate(questions):
        
        question_answer[questions[i]] = [
                answers[i],
                1 if i < 3 else 2
            ]





    def __init__(self) -> None:
        self.models = self.API.list_models(filter="question-answering",sort="downloads",direction=-1,limit=50)
    


    def _url_api(self,url:str):
        """
        La funzione restituisce l'end-point al quale interrogare il modello."""

        #effective:str = url.split("https://huggingface.co")[1]

        return self.common_url+url


    def _generate_input(self,question):

        return {
            "inputs" : {
                "context" : self.context,
                "question" : question
            }
        }
    
    def _valuta_risposta(self,domanda,risposta):

        return self.question_answer[domanda][0] == risposta

    def _fun_obiettivo(self,pesi_locali:dict):

        sum = 0
        for key in pesi_locali:
            if pesi_locali[key]:
                sum = sum + self.question_answer[key][1]
        return sum

    def send_request(self, url,input):

        with self.lock:
            print(f"Processo {multiprocessing.current_process().ident}")
            response = requests.post(url,headers=self.headers,json=input)
            return response

    def _validate(self):

        with open("validator_output1.txt","w") as file:

            #Estraggo dal generator il prossimo modello
            modello:hf_api.ModelInfo = self._next_model()

            #itero finchè ho modell -> modello != None
            while modello:
                
                
                #Estrazione dell'end-point ben formato
                api_url = self._url_api(modello.id)
                print(api_url)

                #dizionario per tenere traccia di quali risposte corrette il modello i-esimo ha fornito
                local = {}

                file.write(f"Il modello {api_url} ha risposto:\n")

                for question in self.question_answer.keys():
                    local[question] = False

                #itero sulle domande presenti
                for question in self.question_answer.keys():

                    #generazione dell'input da inviare all'end-point
                    input = self._generate_input(question)

                    try:
                        #response = self.send_request(api_url,input)
                        first_response = requests.post(api_url,headers=self.headers, json=input)
                        #first_response.raise_for_status()

                        #significa che il modello sta caricando e quindi è necessario attendere.
                        if first_response.status_code == 503:
                            
                            wait = json.loads(first_response.content.decode("utf-8"))["estimated_time"]
                            
                            time.sleep(wait)

                            #response = self.send_request(api_url,input)
                            second_response = requests.post(api_url,headers=self.headers, json=input)

                            if second_response.status_code == 200:

                                risposta = json.loads(second_response.content.decode("utf-8"))["answer"]
                                
                                file.write(f"Domanda {question}, Risposta {risposta}\n")

                                if self._valuta_risposta(question,risposta):
                                    local[question] = True   
                        else:
                            #Se entro in questo branch significa esclusivamente che non ho ottenuto un 503, ma può darsi che abbia ricevuto un 200
                            #oppure un 4xx
                            if first_response.status_code == 200:
                                risposta = json.loads(first_response.content.decode("utf-8"))["answer"]

                                file.write(f"Domanda {question}, Risposta {risposta}\n")

                                if self._valuta_risposta(question,risposta):
                                    local[question] = True
                                time.sleep(2)
                            else:
                                self.logger.warning(f"Richiesta ralativa a {api_url} ha generato il seguente status code {first_response.status_code} con il seguente errore: \n{json.loads(first_response.content.decode('utf-8'))['error']} ")
                                time.sleep(2)
                    except Exception as e:
                        #TO-DO gestire eccezzione
                        self.logger.warning(f"La richiesta {api_url} ha generato la seguente eccezione \n{e}")
                        time.sleep(2)
                        #Arresta il for sulle question
                        break
                
                if self._fun_obiettivo(local) >= 3:
                    print(local)
                    self.result[api_url] = [key for key in local if not local[key]]

                try:
                    modello = self._next_model()
                except StopIteration as e:
                    break
                
    
    
    def _split_into_chunks(self):

        #n_process = os.cpu_count()
        n_process = 10

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




    def _next_model(self) -> hf_api.ModelInfo:
        return next(self.models)


    def get_result(self):
        return self.result




if __name__ == "__main__":


    urls = []

    try:
        with open("crawler_output4.txt","r") as file:
            for riga in file:
                urls.append(riga.strip())
    except FileNotFoundError as e:
        print("File non trovato")
    
    v = Validator()

    #print(v._url_api("https://huggingface.co/farid1088/GQA_RoBERTa_German_legal_SQuAD_part_augmented_2000 "))


    
    v._validate()

    print(v.get_result())
