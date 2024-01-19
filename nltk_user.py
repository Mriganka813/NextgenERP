from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import stopwords
import nltk

app = FastAPI()

class UserInput(BaseModel):
    text: str

# Download NLTK resources (you can also do this manually outside of the code)
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

@app.post("/process_input")
def process_input_api(user_input: UserInput):
    try:
        text = user_input.text
        words = word_tokenize(text)
        sentences = sent_tokenize(text)
        stop_words = set(stopwords.words('english'))
        filtered_words = [word for word in words if word.lower() not in stop_words]
        user_str = str(filtered_words)
        return {"filtered_text": user_str}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
