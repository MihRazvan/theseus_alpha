from openai import OpenAI
from dotenv import load_dotenv
import os

# Load environment variables from .env
load_dotenv()

# Initialize the OpenAI client
client = OpenAI()

def test_openai_connection():
    try:
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are a trading assistant for crypto markets."},
                {"role": "user", "content": "Give me a one-sentence example of a trading insight."}
            ]
        )
        print("✅ OpenAI Connection Successful!")
        print("Response:", completion.choices[0].message.content)
        return True
    except Exception as e:
        print("❌ OpenAI Connection Failed!")
        print("Error:", str(e))
        return False

if __name__ == "__main__":
    test_openai_connection()