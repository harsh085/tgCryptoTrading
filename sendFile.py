import requests
from config import TOKEN
from datetime import datetime
import pandas as pd

def fun(file):
    try:
        base_url = f"https://api.telegram.org/bot{TOKEN}/sendDocument"
        # my_file = open("/DATA/harshit_2311ai52/tgBot/csv_files/"+file, "rb")
        my_file = open(file, "rb")      # full_path
        filename = datetime.now().strftime(file.replace('.csv','').split(r'/')[-1]+"_%d%b%y.csv").lower()
        parameters = {
            "chat_id" : "-1002173444693",
            "caption" : filename
        }

        files = {
            "document" : (filename, my_file)
        }

        resp = requests.get(base_url, data = parameters, files=files)
        print(resp.text)
        return f"{filename} : success\n"
    except Exception as e:
        return str(e)


    


