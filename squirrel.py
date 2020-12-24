import json
import sys
import time
import logging
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from pymongo import MongoClient

conn_str = open('.mongo', 'r').read().strip()
client = MongoClient(conn_str)
db = client.dump1090

def read_and_insert(event):
    data = {}
    with open('aircraft.json', 'r') as fd:
        raw = fd.read()
        if len(raw.strip()) < 10:
            return
        data = json.loads(raw)

    if db.aircraft.find_one({'now': data['now']}) is None:
        item = db.aircraft.insert_one(data)
        print(f'inserted {data["now"]} with id {item.inserted_id}')
    else:
        print(f'skipping insert for {data["now"]}, already stored')

if __name__ == '__main__':
    data = {}
    with open('aircraft.json', 'r') as fd:
        data = json.loads(fd.read())

    if db.aircraft.find_one({'now': data['now']}) is None:
        item = db.aircraft.insert_one(data)
        print(f'inserted {data["now"]} with id {item.inserted_id}')
    else:
        print(f'skipping insert for {data["now"]}, already stored')
    patterns = "*json"
    ignore_patterns = ""
    ignore_directories = True
    case_sensitive = True
    my_event_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    my_event_handler.on_created = read_and_insert
    my_event_handler.on_modified = read_and_insert
    path = "."
    go_recursively = True
    my_observer = Observer()
    my_observer.schedule(my_event_handler, path, recursive=go_recursively)
    my_observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        my_observer.stop()
        my_observer.join()