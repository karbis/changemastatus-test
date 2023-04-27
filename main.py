from fastapi import FastAPI
import requests
import json
from pydantic import BaseModel
from better_profanity import profanity
import os
from fastapi.middleware.cors import CORSMiddleware
import emoji
import time
import threading


def is_emoji(text):
    return text in emoji.EMOJI_DATA

profanity.load_censor_words_from_file('swearlist.txt')

def check_word(string):
    string = ''.join([' ' if not c.isalpha() else c for c in string])
    words = string.split()
    for word in words:
        for i in range(len(word)-3):
            subword = word[i:i+4]
            unique_chars = set(subword)
            if len(unique_chars) == 2 and any(subword.count(c) >= 2 for c in unique_chars):
                return True
    return False

def check_word2(string):
    words = string.split()
    for word in words:
        word = ''.join(['' if not c.isalpha() else c for c in word])
        for i in range(len(word)-3):
            subword = word[i:i+4]
            unique_chars = set(subword)
            if len(unique_chars) == 2 and any(subword.count(c) >= 2 for c in unique_chars):
                return True
    return False

app = FastAPI()
T = os.environ["token"]

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Item(BaseModel):
    status: str
    emoji: str | None = None

@app.get("/")
def read_root():
    return {"Hello": "World"}

rateLimit = False

def doRateLimit(info):
    global rateLimit
    rateLimit = True
    time.sleep(3)
    rateLimit = False

@app.post("/change/")
def read_item(data: Item):
    if rateLimit:
        return 401
    if profanity.contains_profanity(data.status) or check_word(data.status)  or check_word2(data.status):
        return 403
    elif data.emoji != None and not is_emoji(data.emoji):
        return 402
    dicti = {"custom_status":{"text":data.status}}
    if data.emoji != None:
        dicti = {"custom_status":{"text":data.status,"emoji_name":data.emoji}}
    response = requests.patch("https://discord.com/api/v9/users/@me/settings", headers={"authorization": T,"content-type": "application/json"}, data=json.dumps(dicti))
    thread = threading.Thread(target=doRateLimit, args=(response.headers,))
    thread.start()
    return 200
