from fastapi import FastAPI, Request
import requests
import json
from pydantic import BaseModel
from better_profanity import profanity
import os
from fastapi.middleware.cors import CORSMiddleware
import emoji
import time
import threading
import re

def replace_similar_chars(text):
    replacements = {
        'à': 'a',
        'á': 'a',
        'â': 'a',
        'ã': 'a',
        'ä': 'a',
        'å': 'a',
        'æ': 'ae',
        'ç': 'c',
        'è': 'e',
        'é': 'e',
        'ê': 'e',
        'ë': 'e',
        'ì': 'i',
        'í': 'i',
        'î': 'i',
        'ï': 'i',
        'ñ': 'n',
        'ò': 'o',
        'ó': 'o',
        'ô': 'o',
        'õ': 'o',
        'ö': 'o',
        'ø': 'o',
        'œ': 'oe',
        'ß': 'b',
        'ù': 'u',
        'ú': 'u',
        'û': 'u',
        'ü': 'u',
        'ý': 'y',
        'ÿ': 'y',
        'ć': 'c',
        'ĉ': 'c',
        'ċ': 'c',
        'č': 'c',
        'đ': 'd',
        'ē': 'e',
        'ė': 'e',
        'ę': 'e',
        'ě': 'e',
        'ĝ': 'g',
        'ğ': 'g',
        'ġ': 'g',
        'ģ': 'g',
        'ĥ': 'h',
        'ī': 'i',
        'į': 'i',
        'ı': 'i',
        'ĳ': 'ij',
        'ĵ': 'j',
        'ķ': 'k',
        'ĺ': 'l',
        'ļ': 'l',
        'ľ': 'l',
        'ŀ': 'l',
        'ł': 'l',
        'ń': 'n',
        'ņ': 'n',
        'ň': 'n',
        'ŉ': 'n',
        'ō': 'o',
        'ŏ': 'o',
        'ő': 'o',
        'œ': 'oe',
        'ŕ': 'r',
        'ŗ': 'r',
        'ř': 'r',
        'ś': 's',
        'ŝ': 's',
        'ş': 's',
        'š': 's',
        'ţ': 't',
        'ť': 't',
        'ŧ': 't',
        'ū': 'u',
        'ŭ': 'u',
        'ů': 'u',
        'ű': 'u',
        'ų': 'u',
        'ŵ': 'w',
        'ŷ': 'y',
        'ź': 'z',
        'ż': 'z',
        'ž': 'z'
    }
    pattern = re.compile("|".join(replacements.keys()))
    return pattern.sub(lambda m: replacements[m.group()], text)

def is_emoji(text):
    return text in emoji.EMOJI_DATA

def getIp(request: Request):
    x = 'x-forwarded-for'.encode('utf-8')
    for header in request.headers.raw:
        if header[0] == x:
            return re.split(", ",header[1].decode("utf-8"))[0]

profanity.load_censor_words_from_file('swearlist.txt')

def check_word(string):
    string = replace_similar_chars(string)
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
    string = replace_similar_chars(string)
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
lastStatus = ""

def doRateLimit(info):
    global rateLimit
    rateLimit = True
    time.sleep(3.5)
    rateLimit = False

@app.post("/change/")
def read_item(data: Item, request: Request):
    blacklistedIps = re.split(",",os.environ["blacklist"])
    if getIp(request) in blacklistedIps:
        return 406
    global lastStatus
    if lastStatus == data.status:
        return 405
    if rateLimit:
        return 401
    if profanity.contains_profanity(replace_similar_chars(data.status)) or check_word(data.status)  or check_word2(data.status):
        return 403
    elif data.emoji != None and not is_emoji(data.emoji):
        return 402
    dicti = {"custom_status":{"text":data.status}}
    if data.emoji != None:
        dicti = {"custom_status":{"text":data.status,"emoji_name":data.emoji}}
    lastStatus = data.status
    print("Ip (for blacklisting): " + getIp(request))
    print("Status: " + data.status)
    response = requests.patch("https://discord.com/api/v9/users/@me/settings", headers={"authorization": T,"content-type": "application/json"}, data=json.dumps(dicti))
    thread = threading.Thread(target=doRateLimit, args=(response.headers,))
    thread.start()
    return 200
