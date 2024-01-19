from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import re

app = FastAPI()

class UserInput(BaseModel):
    text: str

def process_input(user_table: str):
    pattern = re.compile(r'(\w+)\s+([A-Za-z0-9\s]+)')
    matches = pattern.findall(user_table)
    result_dict = dict(matches)
    return result_dict

@app.post("/process_input")
def process_input_api(user_input: UserInput):
    try:
        result_dict = process_input(user_input.text)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
