from openai import OpenAI
import os
from dotenv import load_dotenv
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def classify_intent(msg: str) -> str:
    prompt = f"""
Classify the intent of the following message as "email" or "music" based on if it is a communication related query or a music/playing a song related query. 
Message: "{msg}"
Respond with only one word: email or music.
"""
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )
    return response.choices[0].message.content.strip().lower()
