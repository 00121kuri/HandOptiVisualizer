from pymongo import MongoClient
import os
from dotenv import load_dotenv
import pandas as pd

load_dotenv(override=True)
DB_IP = os.getenv("DB_IP")
DB_PORT = int(os.getenv("DB_PORT"))
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
print(f"Connect to {DB_IP}")


def get_db():
    client = MongoClient(f'mongodb://{DB_USER}:{DB_PASS}@{DB_IP}:{DB_PORT}/')
    db = client[DB_NAME]
    return db

def get_all_optiSettings():
    db = get_db()
    settings = db['opti-setting'].find()
    return pd.DataFrame(list(settings))

def get_all_envSettings():
    db = get_db()
    settings = db['env-setting'].find()
    return pd.DataFrame(list(settings))

def get_all_dateTime():
    db = get_db()
    dateTimes = db['input'].distinct('dateTime')
    return dateTimes

def get_optiSetting(hash):
    db = get_db()
    optiSetting = db['opti-setting'].find_one({'_id': hash})
    return optiSetting

def get_all_sequenceIds():
    db = get_db()
    sequenceIds = db['result'].distinct('sequenceId')
    return sequenceIds