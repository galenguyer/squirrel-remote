import json
import urllib.request
import time
import os
from os.path import join, dirname

from pymongo import MongoClient
from dotenv import load_dotenv

dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

conn_str = os.getenv('MONGO_URI')
client = MongoClient(conn_str)
db = client.dump1090

def read_and_insert():
    data = {}
    with urllib.request.urlopen("https://planes.galenguyer.com/data/aircraft.json") as url:
        raw = url.read().decode()
        if len(raw.strip()) < 10:
            return
        data = json.loads(raw)

    if db.aircraft.find_one({'now': data['now']}) is None:
        item = db.aircraft.insert_one(data)
        print(f'inserted {data["now"]} with id {item.inserted_id}')
    else:
        print(f'skipping insert for {data["now"]}, already stored')

if __name__ == '__main__':
    while True:
        read_and_insert()