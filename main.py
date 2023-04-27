from fastapi import FastAPI
import requests
import json
from pydantic import BaseModel
from better_profanity import profanity
import os

def check_word(string):
    words = string.split()
    result = []
    for word in words:
        has_property = True
        for i in range(0, len(word)-3, 4):
            if len(set(word[i:i+4])) != 2:
                has_property = False
                break
        result.append(has_property)
    return result

app = FastAPI()
T = os.environ["token"]

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
