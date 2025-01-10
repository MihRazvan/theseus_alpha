import os
import pytest
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

def test_openai_connection():
    """Test if we can connect to OpenAI API."""
    client = OpenAI()
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": "Say hi!"}],
            max_tokens=10
        )
        assert response.choices[0].message.content is not None
    except Exception as e:
        pytest.fail(f"OpenAI API call failed: {str(e)}")

def test_env_variables():
    """Test if environment variables are properly loaded."""
    assert os.getenv("OPENAI_API_KEY") is not None, "OPENAI_API_KEY not found in environment"