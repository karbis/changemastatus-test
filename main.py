from fastapi import FastAPI
import requests
import json
from pydantic import BaseModel
from better_profanity import profanity
import os
from fastapi.middleware.cors import CORSMiddleware

def check_word(string):
    words = string.split()
    result = []
    for word in words:
        has_property = False
        for i in range(len(word)-3):
            subword = word[i:i+4]
            subword = ''.join(filter(str.isalpha, subword))
            unique_chars = set(subword)
            if len(unique_chars) == 2 and any(subword.count(c) >= 2 for c in unique_chars):
                has_property = True
                break
        result.append(has_property)
    return result

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

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.post("/change/")
def read_item(data: Item):
    if profanity.contains_profanity(data.status) or check_word(data.status):
        return 403
    requests.patch("https://discord.com/api/v9/users/@me/settings", headers={"authorization": T,"content-type": "application/json"}, data=json.dumps({"custom_status":{"text":data.status}}))
    return 200
